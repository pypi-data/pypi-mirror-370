"""
Response type definitions for the Agent SDK.

This module provides all response models returned by SDK operations.
All models use strict Pydantic validation for type safety.
"""

from pydantic import BaseModel, ConfigDict, Field


class SignAndSendResponse(BaseModel):
    """
    Standard response from sign_and_send operations.

    This response is returned after successfully signing and broadcasting
    a transaction through the Circuit backend.

    Attributes:
        internal_transaction_id: Internal transaction ID for tracking
        tx_hash: Transaction hash once broadcast to the network
        transaction_url: Optional transaction URL (explorer link)

    Example:
        ```python
        response = await sdk.sign_and_send({
            "network": "ethereum:1",
            "request": {"toAddress": "0x...", "data": "0x", "value": "0"}
        })
        print(f"Transaction hash: {response.tx_hash}")
        if response.transaction_url:
            print(f"View on explorer: {response.transaction_url}")
        ```
    """

    internal_transaction_id: int = Field(
        ..., description="Internal transaction ID for tracking"
    )
    tx_hash: str = Field(..., description="Transaction hash once broadcast")
    transaction_url: str | None = Field(
        None, description="Optional transaction URL (explorer link)"
    )

    model_config = ConfigDict(extra="forbid")


class BalanceResponse(BaseModel):
    """
    Balance response with amount, decimals, and token flag.

    This response provides comprehensive balance information that can be
    used for display or further calculations.

    Attributes:
        amount: Raw amount as string (wei, lamports, or token units)
        decimals: Number of decimals for the asset
        is_token: Whether this is a token (True) or native asset (False)

    Example:
        ```python
        balance = await sdk.utils.get_balance({
            "network": "ethereum:1",
            "address": "0x..."
        })

        # Format for display
        formatted = sdk.utils.format_token_amount(
            int(balance.amount),
            balance.decimals
        )
        asset_type = "token" if balance.is_token else "native"
        print(f"Balance: {formatted} ({asset_type})")
        ```
    """

    amount: str = Field(
        ..., description="Raw amount as string (wei, lamports, or token units)"
    )
    decimals: int = Field(
        ...,
        description="Number of decimals for the asset",
        ge=0,  # Must be non-negative
    )
    is_token: bool = Field(
        ..., description="Whether this is a token (True) or native asset (False)"
    )

    model_config = ConfigDict(extra="forbid")
