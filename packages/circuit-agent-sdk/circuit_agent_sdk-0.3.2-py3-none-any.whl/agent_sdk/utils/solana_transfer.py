"""
Solana transfer utilities for the SDK.

These are internal implementations used by AgentUtils.transfer().
Users should not call these functions directly, but instead use:

    await sdk.utils.transfer({
        "network": "solana",
        "from_address": "...",
        "to_address": "...",
        "amount": "1000000",  # lamports for SOL, base units for SPL
        "mint": "...",  # Optional: include for SPL transfers
        "decimals": 6,  # Required when mint is provided
        "message": "Transfer demo"
    })
"""

from collections.abc import Awaitable, Callable

from ..types import SignAndSendRequest, SignAndSendResponse
from ..types.requests import SolanaSignRequest
from .solana import (
    create_native_sol_transfer_transaction,
    create_spl_token_transfer_transaction,
)


async def transfer_solana_native(
    from_address: str,
    to_address: str,
    lamports: str,
    rpc_url: str,
    sign_and_send: Callable[[SignAndSendRequest], Awaitable[SignAndSendResponse]],
    message: str | None = None,
) -> SignAndSendResponse:
    """
    Transfer native SOL using our working implementation.
    This is an internal function used by AgentUtils.transfer().

    Args:
        from_address: Sender's Solana address (base58)
        to_address: Recipient's Solana address (base58)
        lamports: Amount to send in lamports (as string)
        rpc_url: RPC URL for the Solana network
        sign_and_send: Function to call for signing and sending
        message: Optional message to include with the transaction

    Returns:
        SignAndSendResponse with transaction hash

    Example:
        Users should not call this directly. Instead use:
        ```python
        await sdk.utils.transfer({
            "network": "solana",
            "from_address": "...",
            "to_address": "...",
            "amount": "1000000",  # lamports
            "message": "SOL transfer demo"
        })
        ```
    """
    # Create the unsigned transaction
    unsigned_hex = await create_native_sol_transfer_transaction(
        from_address=from_address,
        to_address=to_address,
        lamports=int(lamports),
        rpc_url=rpc_url,
    )

    # Send it to circuit for signing and broadcasting
    # Use dict to construct the request to work with aliased field
    return await sign_and_send(
        SignAndSendRequest(
            network="solana",
            request=SolanaSignRequest.model_validate({"hexTransaction": unsigned_hex}),
            message=message,
        )
    )


async def transfer_solana_token(
    from_address: str,
    to_address: str,
    mint: str,
    amount: str,
    decimals: int,
    rpc_url: str,
    sign_and_send: Callable[[SignAndSendRequest], Awaitable[SignAndSendResponse]],
    message: str | None = None,
) -> SignAndSendResponse:
    """
    Transfer SPL tokens.
    This is an internal function used by AgentUtils.transfer().
    Currently a placeholder until we implement SPL transfers.

    Args:
        from_address: Token owner's address (base58)
        to_address: Recipient's address (base58)
        mint: SPL token mint address (base58)
        amount: Amount to send in base units (as string)
        decimals: Number of decimals for the token
        rpc_url: RPC URL for the Solana network
        sign_and_send: Function to call for signing and sending
        message: Optional message to include with the transaction

    Returns:
        SignAndSendResponse with transaction hash

    Example:
        Users should not call this directly. Instead use:
        ```python
        await sdk.utils.transfer({
            "network": "solana",
            "from_address": "...",
            "to_address": "...",
            "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
            "amount": "1000000",  # 1 USDC (6 decimals)
            "decimals": 6,
            "message": "USDC transfer demo"
        })
        ```

    Implementation Plan:
    1. Find token account for owner+mint (get_token_accounts_by_owner)
    2. Create transfer_checked instruction (Token.transfer_checked_ix)
    3. Build and sign transaction like native transfer
    4. Send to Circuit for signing/broadcast
    """
    # Create the unsigned transaction
    unsigned_hex = await create_spl_token_transfer_transaction(
        from_address=from_address,
        to_address=to_address,
        mint=mint,
        amount=int(amount),
        rpc_url=rpc_url,
    )

    # Send it to circuit for signing and broadcasting
    # Use dict to construct the request to work with aliased field
    return await sign_and_send(
        SignAndSendRequest(
            network="solana",
            request=SolanaSignRequest.model_validate({"hexTransaction": unsigned_hex}),
            message=message,
        )
    )
