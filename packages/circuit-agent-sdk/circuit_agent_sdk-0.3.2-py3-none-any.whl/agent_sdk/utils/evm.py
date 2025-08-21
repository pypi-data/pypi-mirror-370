"""
EVM-specific utility implementations using web3.py.

This module provides functions for interacting with EVM-compatible blockchains
using the web3.py library for balance checking and other read operations.
"""

from web3 import Web3
from web3.contract import Contract
from web3.exceptions import ContractLogicError

from ..types.responses import BalanceResponse

# Standard ERC-20 ABI for balanceOf and decimals methods
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function",
    },
]


async def get_evm_native_balance(address: str, rpc_url: str) -> BalanceResponse:
    """
    Get native EVM balance (wei) using web3.py.

    Args:
        address: Address to check balance for
        rpc_url: RPC URL for the EVM network

    Returns:
        BalanceResponse with amount in wei, 18 decimals, and is_token=False

    Example:
        ```python
        balance = await get_evm_native_balance(
            "0x742d35cc6634C0532925a3b8D65e95f32B6b5582",
            "https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY"
        )
        print(f"Balance: {balance.amount} wei")
        ```
    """
    # Initialize web3 with the RPC URL
    w3 = Web3(Web3.HTTPProvider(rpc_url))

    # Validate address format
    if not Web3.is_address(address):
        raise ValueError(f"Invalid Ethereum address: {address}")

    # Convert to checksum address
    checksum_address = Web3.to_checksum_address(address)

    # Get balance in wei
    balance_wei = w3.eth.get_balance(checksum_address)

    return BalanceResponse(amount=str(balance_wei), decimals=18, is_token=False)


async def get_evm_token_balance(
    address: str, token: str, rpc_url: str
) -> BalanceResponse:
    """
    Get ERC-20 token balance using web3.py.

    Args:
        address: Address to check balance for
        token: ERC-20 token contract address
        rpc_url: RPC URL for the EVM network

    Returns:
        BalanceResponse with token balance and decimals from the contract

    Example:
        ```python
        balance = await get_evm_token_balance(
            "0x742d35cc6634C0532925a3b8D65e95f32B6b5582",
            "0xA0b86a33E6441d9c9C4c5f5b3E6b8e8c0f0f9d1a",  # USDC
            "https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY"
        )
        print(f"USDC Balance: {balance.amount} (decimals: {balance.decimals})")
        ```
    """
    # Initialize web3 with the RPC URL
    w3 = Web3(Web3.HTTPProvider(rpc_url))

    # Validate addresses
    if not Web3.is_address(address):
        raise ValueError(f"Invalid Ethereum address: {address}")
    if not Web3.is_address(token):
        raise ValueError(f"Invalid token contract address: {token}")

    # Convert to checksum addresses
    checksum_address = Web3.to_checksum_address(address)
    checksum_token = Web3.to_checksum_address(token)

    # Create contract instance
    contract: Contract = w3.eth.contract(address=checksum_token, abi=ERC20_ABI)

    # Get balance
    try:
        balance = contract.functions.balanceOf(checksum_address).call()
    except ContractLogicError:
        # If balanceOf fails, return 0
        balance = 0

    # Get decimals
    try:
        decimals = contract.functions.decimals().call()
    except (ContractLogicError, Exception):
        # If decimals() is not implemented or fails, default to 18
        decimals = 18

    return BalanceResponse(amount=str(balance), decimals=decimals, is_token=True)
