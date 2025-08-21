"""
Solana-specific utility implementations using solana-py.

This module provides functions for interacting with the Solana network
using the solana-py library for balance checking and other operations.
"""

from typing import Any, cast

import spl.token.instructions as spl_token
from solana.rpc.api import Client
from solana.rpc.commitment import Confirmed
from solana.rpc.types import TokenAccountOpts
from solders.message import Message
from solders.null_signer import NullSigner
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from solders.transaction import VersionedTransaction

from ..types.responses import BalanceResponse


async def get_solana_native_balance(address: str, rpc_url: str) -> BalanceResponse:
    """
    Get native SOL balance (lamports) using solana-py.

    Args:
        address: Solana address to check balance for (base58)
        rpc_url: RPC URL for the Solana network

    Returns:
        BalanceResponse with amount in lamports, 9 decimals, and is_token=False

    Example:
        ```python
        balance = await get_solana_native_balance(
            "9WbZXa5bAz1kMKKJM8jbLbmr6NZrJ3q8JM8jdN9QmQmE",
            "https://api.mainnet-beta.solana.com"
        )
        print(f"SOL Balance: {balance.amount} lamports")
        ```
    """
    # Initialize Solana client
    client = Client(rpc_url)
    try:
        # Convert address string to Pubkey
        pubkey = Pubkey.from_string(address)
    except Exception as e:
        raise ValueError(f"Invalid Solana address: {address}") from e
    # Get balance
    response = client.get_balance(pubkey, commitment=Confirmed)
    if response.value is None:
        raise ValueError(f"Failed to get balance for address: {address}")
    # Balance is returned in lamports
    amount = response.value
    return BalanceResponse(amount=str(amount), decimals=9, is_token=False)


async def get_solana_token_balance(
    owner: str, mint: str, rpc_url: str
) -> BalanceResponse:
    """
    Get SPL token balance for owner+mint using solana-py.

    Args:
        owner: Owner address (base58)
        mint: Token mint address (base58)
        rpc_url: RPC URL for the Solana network

    Returns:
        BalanceResponse with token balance and decimals

    Example:
        ```python
        balance = await get_solana_token_balance(
            "9WbZXa5bAz1kMKKJM8jbLbmr6NZrJ3q8JM8jdN9QmQmE",
            "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC mint
            "https://api.mainnet-beta.solana.com"
        )
        print(f"Token Balance: {balance.amount} (decimals: {balance.decimals})")
        ```
    """
    # Initialize Solana client
    client = Client(rpc_url)
    try:
        # Convert address strings to Pubkeys
        owner_pubkey = Pubkey.from_string(owner)
        mint_pubkey = Pubkey.from_string(mint)
    except Exception as e:
        raise ValueError(f"Invalid Solana address: {e}") from e
    # Get token accounts by owner and mint
    # Create the opts parameter correctly for solana-py
    opts = TokenAccountOpts(mint=mint_pubkey)
    # Get token accounts - this returns parsed JSON data
    response = client.get_token_accounts_by_owner_json_parsed(
        owner_pubkey, opts, commitment=Confirmed
    )
    if not response.value:
        # No token accounts found, return 0 balance
        return BalanceResponse(amount="0", decimals=0, is_token=True)
    # Sum balances across all token accounts and get decimals
    total_amount = 0
    decimals = 0
    for account_info in response.value:
        if account_info.account and account_info.account.data:
            # Access the parsed data correctly
            # The data is in account_info.account.data.parsed (dict)
            parsed = cast(dict[str, Any], account_info.account.data.parsed)
            if isinstance(parsed, dict) and "info" in parsed:
                info = cast(dict[str, Any], parsed["info"])
                # Get token amount information
                if "tokenAmount" in info:
                    token_amount = cast(dict[str, Any], info["tokenAmount"])
                    # Extract amount as string and convert to int
                    amount_str = cast(str, token_amount.get("amount", "0"))
                    amount = int(amount_str)
                    total_amount += amount
                    # Get decimals (should be same for all accounts of same mint)
                    if "decimals" in token_amount:
                        decimals = cast(int, token_amount["decimals"])
    return BalanceResponse(amount=str(total_amount), decimals=decimals, is_token=True)


async def create_native_sol_transfer_transaction(
    from_address: str, to_address: str, lamports: int, rpc_url: str
) -> str:
    """
    Create an unsigned native SOL transfer transaction.
    This is the exact implementation that was working in our test code.

    Args:
        from_address: Sender's Solana address (base58)
        to_address: Recipient's Solana address (base58)
        lamports: Amount to send in lamports
        rpc_url: RPC URL for the Solana network

    Returns:
        Hex string of the unsigned transaction
    """
    # Initialize RPC client
    rpc = Client(rpc_url)

    # Get latest blockhash
    latest = rpc.get_latest_blockhash()

    # Convert addresses to PublicKey
    from_pubkey = Pubkey.from_string(from_address)
    to_pubkey = Pubkey.from_string(to_address)

    # Create transfer instruction
    transfer_instruction = transfer(
        TransferParams(from_pubkey=from_pubkey, to_pubkey=to_pubkey, lamports=lamports)
    )

    # Create transaction message
    message = Message.new_with_blockhash(
        instructions=[transfer_instruction],
        payer=from_pubkey,
        blockhash=latest.value.blockhash,
    )

    # Create unsigned transaction
    null_signer = NullSigner(from_pubkey)
    empty_signatures = [null_signer]
    unsigned_tx = VersionedTransaction(message, empty_signatures)

    # Serialize to hex
    return bytes(unsigned_tx).hex()


async def create_spl_token_transfer_transaction(
    from_address: str, to_address: str, mint: str, amount: int, rpc_url: str
) -> str:
    """
    Create an unsigned SPL token transfer transaction.
    This implementation matches our working test code.

    Args:
        from_address: Token owner's Solana address (base58)
        to_address: Recipient's Solana address (base58)
        mint: SPL token mint address (base58)
        amount: Amount to send in base units
        rpc_url: RPC URL for the Solana network

    Returns:
        Hex string of the unsigned transaction

    Raises:
        Exception: If token account not found or other errors occur
    """
    # Initialize RPC client
    rpc = Client(rpc_url)

    # Get latest blockhash
    latest = rpc.get_latest_blockhash()

    # Setup addresses
    fee_payer = Pubkey.from_string(from_address)
    mint_pubkey = Pubkey.from_string(mint)

    # Get source token account
    token_filter = TokenAccountOpts(mint=mint_pubkey)
    response = rpc.get_token_accounts_by_owner_json_parsed(fee_payer, token_filter)
    token_accounts = response.value

    if not token_accounts:
        raise Exception("No token account found for mint")

    # Get source token account pubkey and info
    source_token_account = token_accounts[0].pubkey

    # Get destination token account
    dest_response = rpc.get_token_accounts_by_owner_json_parsed(
        Pubkey.from_string(to_address), token_filter
    )
    dest_token_accounts = dest_response.value

    if not dest_token_accounts:
        raise Exception("No destination token account found for mint")

    dest_token_account = dest_token_accounts[0].pubkey

    # Check which token program owns the account (Token vs Token-2022)
    account_info = rpc.get_account_info(source_token_account).value
    if not account_info:
        raise Exception("Could not get token account info")

    program_id = account_info.owner

    # Get decimals from parsed account data
    account_data = cast(dict[str, Any], token_accounts[0].account.data.parsed)
    parsed_data = cast(dict[str, Any], account_data["info"])
    token_amount_data = cast(dict[str, Any], parsed_data["tokenAmount"])
    decimals = cast(int, token_amount_data["decimals"])

    # Create transfer_checked instruction
    transfer_instruction = spl_token.transfer_checked(
        spl_token.TransferCheckedParams(
            program_id=program_id,
            source=source_token_account,
            mint=mint_pubkey,
            dest=dest_token_account,
            owner=fee_payer,
            amount=amount,
            decimals=decimals,
        )
    )

    # Create transaction message
    message = Message.new_with_blockhash(
        instructions=[transfer_instruction],
        payer=fee_payer,
        blockhash=latest.value.blockhash,
    )

    # Create unsigned transaction
    null_signer = NullSigner(fee_payer)
    empty_signatures = [null_signer]
    unsigned_tx = VersionedTransaction(message, empty_signatures)

    # Serialize to hex
    return bytes(unsigned_tx).hex()
