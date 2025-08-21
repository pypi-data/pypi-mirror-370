"""
Utility helpers surfaced as `agent.utils`.

These helpers rely on user-supplied RPC URLs (see `SDKConfig.connections`) for
read operations and simple client-side transaction building. For writes, they
usually delegate to `AgentSdk.sign_and_send()` to perform signing and
broadcasting via the backend.
"""

import logging
import re
import sys
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any

import toml

from ..types import SignAndSendRequest, SignAndSendResponse

if TYPE_CHECKING:
    from ..client import APIClient

# Type for the sign_and_send function that utils need to call
SignAndSendFunction = Callable[[SignAndSendRequest], Awaitable[SignAndSendResponse]]


# class AgentUtils:
#     """
#     Utility helper interface exposed via `AgentSdk.utils`.

#     Provides cross-chain utilities for common operations like checking balances,
#     transferring tokens, and formatting amounts for display.

#     Example:
#         ```python
#         # Usually accessed via AgentSdk instance
#         from agent_sdk import AgentSdk, SDKConfig, SDKConnections

#         sdk = AgentSdk(SDKConfig(
#             session_id=123,
#             connections=SDKConnections(
#                 evm={1: "https://eth-rpc.com"},
#                 solana="https://api.mainnet-beta.solana.com"
#             )
#         ))

#         # Check balance
#         balance = await sdk.utils.get_balance({
#             "network": "ethereum:1",
#             "address": "0x742d35cc6634C0532925a3b8D65e95f32B6b5582"
#         })

#         # Format for display
#         formatted = sdk.utils.format_token_amount(
#             int(balance.amount),
#             balance.decimals
#         )
#         ```
#     """

#     def __init__(
#         self, client: "APIClient", config: SDKConfig, sign_and_send: SignAndSendFunction
#     ) -> None:
#         """
#         Initialize AgentUtils.

#         Args:
#             client: API client for backend communication
#             config: SDK configuration
#             sign_and_send: Function to call for transaction signing/broadcasting
#         """
#         self.client = client
#         self.config = config
#         self.sign_and_send = sign_and_send

#     async def get_balance(self, request: GetBalanceRequest | dict) -> BalanceResponse:
#         """
#         Get the balance for a native asset or token.

#         - For EVM, provide network="ethereum:chainId" and optionally token
#           for an ERC-20. Uses the configured RPC provider for the target chain.
#         - For Solana, provide network="solana" and optionally mint for an SPL
#           token. Uses connections.solana or defaults to public mainnet.

#         Args:
#             request: Cross-chain balance query (GetBalanceRequest or dict)

#         Returns:
#             Balance response with amount, decimals, and token flag

#         Raises:
#             ValueError: If no RPC URL is configured for the requested network

#         Example:
#             ```python
#             # EVM — native balance
#             eth_bal = await sdk.utils.get_balance({
#                 "network": "ethereum:42161",
#                 "address": "0xabc...",
#             })

#             # EVM — ERC-20 token balance
#             usdc_bal = await sdk.utils.get_balance({
#                 "network": "ethereum:42161",
#                 "address": "0xabc...",
#                 "token": "0xA0b86a33E6441d9c9C4c5f5b3E6b8e8c0f0f9d1a",
#             })

#             # Solana — native SOL balance (lamports)
#             sol_bal = await sdk.utils.get_balance({
#                 "network": "solana",
#                 "address": "YourBase58Address",
#             })

#             # Solana — SPL token balance
#             spl_bal = await sdk.utils.get_balance({
#                 "network": "solana",
#                 "address": "YourBase58Address",
#                 "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
#             })
#             ```
#         """
#         # Handle both dict and Pydantic model inputs
#         if isinstance(request, dict):
#             request_obj = GetBalanceRequest(**request)
#         else:
#             request_obj = request
#         if is_ethereum_network(request_obj.network):
#             chain_id = get_chain_id_from_network(request_obj.network)
#             rpc_url = (
#                 self.config.connections.evm.get(chain_id)
#                 if self.config.connections and self.config.connections.evm
#                 else None
#             )

#             if not rpc_url:
#                 raise ValueError(
#                     f"No RPC URL configured for chain {chain_id}. "
#                     f"Add to connections.evm[{chain_id}]"
#                 )

#             # Check if token is provided (works for both Pydantic models and dicts)
#             if request_obj.token:
#                 return await get_evm_token_balance(
#                     address=request_obj.address,
#                     token=request_obj.token,
#                     rpc_url=rpc_url,
#                 )
#             return await get_evm_native_balance(
#                 address=request_obj.address, rpc_url=rpc_url
#             )

#         if is_solana_network(request_obj.network):
#             rpc_url = (
#                 self.config.connections.solana
#                 if self.config.connections and self.config.connections.solana
#                 else "https://api.mainnet-beta.solana.com"
#             )

#             # Check if mint is provided (works for both Pydantic models and dicts)
#             if request_obj.mint:
#                 return await get_solana_token_balance(
#                     owner=request_obj.address, mint=request_obj.mint, rpc_url=rpc_url
#                 )
#             return await get_solana_native_balance(
#                 address=request_obj.address, rpc_url=rpc_url
#             )

#         raise ValueError(f"Unsupported network: {request_obj.network}")

#     async def transfer(self, request: TransferRequest | dict) -> SignAndSendResponse:
#         """
#         Transfer a native asset or token.

#         Builds the minimal transaction data locally (when needed) and then calls
#         sign_and_send() to execute via the backend.

#         Args:
#             request: Cross-chain transfer parameters
#               - For EVM networks ("ethereum:chainId"):
#                 - to_address is the EVM recipient
#                 - amount is in wei (as a string)
#                 - Optional token (ERC-20 contract) switches to token transfer; omit for native ETH
#                 - Optional message (short string) will be persisted along with the transaction
#               - For Solana ("solana"):
#                 - from_address is required (the fee payer and source)
#                 - to_address is the recipient (base58)
#                 - amount is in raw units as a string
#                   - Native SOL uses lamports (1 SOL = 1e9 lamports)
#                   - SPL tokens use base units (e.g., 1 USDC = 1e6 base units for 6 decimals)
#                 - Optional mint indicates an SPL token transfer (omit for native SOL)
#                 - Required decimals when mint is provided (number of decimals for the SPL token)
#                 - Optional message (short string) will be persisted along with the transaction

#         Returns:
#             Standard sign-and-send response including tx_hash

#         Raises:
#             ValueError: If required RPC URLs are not configured

#         Example:
#             ```python
#             # EVM — ERC-20 transfer
#             await sdk.utils.transfer({
#                 "network": "ethereum:42161",
#                 "to_address": "0xrecipient...",
#                 "amount": "1000000",  # 1e6 token units
#                 "token": "0xusdc...",
#                 "message": "ERC20 transfer demo",
#             })

#             # EVM — native transfer
#             await sdk.utils.transfer({
#                 "network": "ethereum:1",
#                 "to_address": "0xrecipient...",
#                 "amount": "1000000000000000000",  # 1 ETH (wei)
#                 "message": "Self-transfer demo",
#             })

#             # Solana — native SOL transfer (lamports)
#             await sdk.utils.transfer({
#                 "network": "solana",
#                 "from_address": "YourBase58Address",
#                 "to_address": "RecipientBase58",
#                 "amount": "100000000",  # 0.1 SOL in lamports
#                 "message": "SOL transfer demo",
#             })

#             # Solana — SPL token transfer
#             await sdk.utils.transfer({
#                 "network": "solana",
#                 "from_address": "YourBase58Address",
#                 "to_address": "RecipientBase58",
#                 "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC mint
#                 "decimals": 6,  # USDC has 6 decimals
#                 "amount": "1000000",  # 1 USDC in base units (1e6)
#                 "message": "SPL transfer demo",
#             })
#             ```
#         """
#         # Handle both dict and Pydantic model inputs
#         if isinstance(request, dict):
#             request_obj = TransferRequest(**request)
#         else:
#             request_obj = request
#         if is_ethereum_network(request_obj.network):
#             chain_id = get_chain_id_from_network(request_obj.network)
#             rpc_url = (
#                 self.config.connections.evm.get(chain_id)
#                 if self.config.connections and self.config.connections.evm
#                 else None
#             )
#             if not rpc_url:
#                 raise ValueError(
#                     f"No RPC URL configured for chain {chain_id}. Transfer requires RPC access."
#                 )

#             # Handle EVM transfer
#             if request_obj.token:
#                 # ERC-20 token transfer - build transfer(address,uint256) calldata
#                 to = request_obj.to_address.lower().replace("0x", "").zfill(64)
#                 amount = hex(int(request_obj.amount))[2:].zfill(64)
#                 transfer_selector = "a9059cbb"  # transfer(address,uint256)
#                 data = f"0x{transfer_selector}{to}{amount}"

#                 return await self.sign_and_send(
#                     SignAndSendRequest(
#                         network=request_obj.network,
#                         request=EthereumSignRequest(
#                             to_address=request_obj.token,
#                             data=data,
#                             value="0",  # No ETH value for token transfers
#                         ),
#                         message=request_obj.message,
#                     )
#                 )
#             else:
#                 # Native ETH transfer
#                 return await self.sign_and_send(
#                     SignAndSendRequest(
#                         network=request_obj.network,
#                         request=EthereumSignRequest(
#                             to_address=request_obj.to_address,
#                             data="0x",
#                             value=request_obj.amount,  # amount in wei
#                         ),
#                         message=request_obj.message,
#                     )
#                 )

#         if is_solana_network(request_obj.network):
#             rpc_url = (
#                 self.config.connections.solana
#                 if self.config.connections and self.config.connections.solana
#                 else "https://api.mainnet-beta.solana.com"
#             )

#             # Solana requires from_address
#             if not request_obj.from_address:
#                 raise ValueError("'from_address' is required for Solana transfers")

#             # Import here to avoid circular dependency
#             from .solana_transfer import transfer_solana_native, transfer_solana_token

#             # Handle Solana transfer (native SOL or SPL token)
#             if request_obj.mint:
#                 # SPL token transfer
#                 if request_obj.decimals is None:
#                     raise ValueError("'decimals' is required for SPL token transfers")

#                 return await transfer_solana_token(
#                     from_address=request_obj.from_address,
#                     to_address=request_obj.to_address,
#                     mint=request_obj.mint,
#                     amount=request_obj.amount,
#                     decimals=request_obj.decimals,
#                     rpc_url=rpc_url,
#                     sign_and_send=self.sign_and_send,
#                     message=request_obj.message,
#                 )
#             else:
#                 # Native SOL transfer
#                 return await transfer_solana_native(
#                     from_address=request_obj.from_address,
#                     to_address=request_obj.to_address,
#                     lamports=request_obj.amount,
#                     rpc_url=rpc_url,
#                     sign_and_send=self.sign_and_send,
#                     message=request_obj.message,
#                 )

#         raise ValueError(f"Unsupported network: {request_obj.network}")

#     def format_token_amount(
#         self,
#         amount: int,
#         decimals: int,
#         subscript_decimals: int = 4,
#         standard_decimals: int = 6,
#     ) -> str:
#         """
#         Human-friendly token formatter for raw integer amounts with decimals.

#         Args:
#             amount: The raw token amount as integer
#             decimals: Token decimals (e.g. 18 for ETH, 6 for USDC)
#             subscript_decimals: Max decimals to show after subscript notation (default: 4)
#             standard_decimals: Max decimals to show for normal numbers (default: 6)

#         Returns:
#             Formatted string like "1,234.567" or "0.0₄9635"

#         Example:
#             ```python
#             # Format large amounts
#             sdk.utils.format_token_amount(123456789, 6)  # "123.456789"

#             # Format small amounts with subscript notation
#             sdk.utils.format_token_amount(1000, 9)  # "0.000₆001"
#             ```
#         """
#         sign = "-" if amount < 0 else ""
#         abs_amount = abs(amount)
#         amount_str = str(abs_amount)

#         has_fraction = decimals > 0
#         if len(amount_str) > decimals:
#             integer_part = amount_str[:-decimals]
#         else:
#             integer_part = "0"

#         if has_fraction:
#             if len(amount_str) > decimals:
#                 fractional = amount_str[-decimals:]
#             else:
#                 fractional = amount_str.zfill(decimals)
#         else:
#             fractional = ""

#         # Add thousands separators to integer part
#         grouped_int = self._add_thousands_separators(integer_part)

#         if not has_fraction:
#             return sign + grouped_int

#         if fractional and not fractional.strip("0"):
#             return sign + grouped_int

#         # Count leading zeros in fractional part
#         leading_zeros = len(fractional) - len(fractional.lstrip("0"))

#         if leading_zeros >= 3:
#             # Use subscript notation for numbers with 3+ leading zeros
#             rest = fractional[leading_zeros:]
#             truncated_rest = rest[:subscript_decimals] if rest else ""
#             compressed_frac = f"0{self._to_subscript(leading_zeros)}{truncated_rest}"
#             return f"{sign}{grouped_int}.{compressed_frac}"

#         # For 0-2 leading zeros, use standard decimal formatting
#         truncated_frac = fractional[:standard_decimals]
#         trimmed_frac = truncated_frac.rstrip("0")  # Remove trailing zeros

#         if not trimmed_frac:
#             return sign + grouped_int
#         return f"{sign}{grouped_int}.{trimmed_frac}"

#     def _add_thousands_separators(self, num_str: str) -> str:
#         """Add comma thousands separators to a number string."""
#         # Use regex to add commas every 3 digits from the right
#         return re.sub(r"(\d)(?=(\d{3})+(?!\d))", r"\1,", num_str)

#     def _to_subscript(self, num: int) -> str:
#         """Convert number to subscript characters."""
#         subscript_map = {
#             "0": "₀",
#             "1": "₁",
#             "2": "₂",
#             "3": "₃",
#             "4": "₄",
#             "5": "₅",
#             "6": "₆",
#             "7": "₇",
#             "8": "₈",
#             "9": "₉",
#         }
#         return "".join(subscript_map.get(c, c) for c in str(num))


# Additional utility functions for Agent configuration and logging


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Set up logging configuration for the SDK

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("circuit_agent")

    # Don't add handlers if they already exist
    if logger.handlers:
        return logger

    # Set level
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    return logger


def read_pyproject_config(project_root: str | None = None) -> dict[str, Any]:
    """
    Read configuration from pyproject.toml

    Args:
        project_root: Path to project root directory. If None, searches upward from current file.

    Returns:
        Dictionary containing project configuration
    """
    if project_root is None:
        # Start from the current file's directory and search upward
        current_path = Path(__file__).parent
        project_root_path = current_path.parent  # Go up from sdk/ to project root
    else:
        project_root_path = Path(project_root)

    pyproject_path = project_root_path / "pyproject.toml"

    if not pyproject_path.exists():
        # Fallback configuration
        return {
            "project": {
                "name": "circuit-agent",
                "description": "A Circuit Agent",
                "version": "1.0.0",
            },
            "tool": {
                "circuit": {"name": "Circuit Agent", "description": "A Circuit Agent"}
            },
        }

    try:
        with open(pyproject_path) as f:
            config = toml.load(f)
        return config
    except Exception as e:
        logger = setup_logging()
        logger.warning(f"Failed to read pyproject.toml: {e}. Using fallback config.")
        return {
            "project": {
                "name": "circuit-agent",
                "description": "A Circuit Agent",
                "version": "1.0.0",
            },
            "tool": {
                "circuit": {"name": "Circuit Agent", "description": "A Circuit Agent"}
            },
        }


def get_agent_config_from_pyproject(
    project_root: str | None = None,
) -> dict[str, str]:
    """
    Extract agent configuration (title, description, version) from pyproject.toml

    Args:
        project_root: Path to project root directory. If None, searches upward from current file.

    Returns:
        Dictionary containing agent configuration
    """
    config = read_pyproject_config(project_root)

    # Extract project info
    project_info = config.get("project", {})
    tool_info = config.get("tool", {}).get("circuit", {})

    return {
        "title": tool_info.get("name", project_info.get("name", "Circuit Agent")),
        "description": tool_info.get(
            "description", project_info.get("description", "A Circuit Agent")
        ),
        "version": project_info.get("version", "1.0.0"),
    }
