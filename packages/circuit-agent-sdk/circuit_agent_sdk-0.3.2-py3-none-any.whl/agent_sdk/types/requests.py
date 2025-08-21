"""
Request type definitions with conditional shapes based on network.

This module provides request models that adapt their required fields based
on the target network, providing type safety while maintaining flexibility.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class AddMessageRequest(BaseModel):
    """
    Message request for add_message function.

    Used to send timeline messages that show up in session traces and UIs for
    observability, human-in-the-loop reviews, and debugging.

    Attributes:
        type: Message type for categorization. Available options:
            • "observe"  - General observations and status updates
            • "validate" - Validation checks and confirmations
            • "reflect"  - Analysis and reasoning about actions
            • "error"    - Error messages and failures
            • "warning"  - Warnings and potential issues
        short_message: Brief message content (max 250 characters)

    Examples:
        ```python
        # Status observation
        await sdk.add_message({
            "type": "observe",
            "short_message": "Starting swap operation"
        })

        # Validation result
        await sdk.add_message({
            "type": "validate",
            "short_message": "Confirmed sufficient balance"
        })

        # Error reporting
        await sdk.add_message({
            "type": "error",
            "short_message": "Transaction failed: insufficient gas"
        })
        ```
    """

    type: Literal["observe", "validate", "reflect", "error", "warning"] = Field(
        ..., description="Type of message for categorization"
    )
    short_message: str = Field(..., description="Brief message content", max_length=250)

    model_config = ConfigDict(extra="forbid")


class EthereumSignRequest(BaseModel):
    """Ethereum-specific transaction request."""

    to_address: str = Field(
        ...,
        description="Recipient address in hex format",
        pattern=r"^0x[a-fA-F0-9]{40}$",
    )
    data: str = Field(
        ..., description="Transaction data in hex format", pattern=r"^0x[a-fA-F0-9]*$"
    )
    value: str = Field(..., description="Transaction value in wei as string")

    model_config = ConfigDict(extra="forbid")


class SolanaSignRequest(BaseModel):
    """Solana-specific transaction request."""

    hex_transaction: str = Field(
        ...,
        alias="hexTransaction",
        description="Serialized VersionedTransaction as hex string",
    )

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class SignAndSendRequest(BaseModel):
    """
    Main sign_and_send request type with network-specific conditional shapes.

    The request shape changes based on the network field:
    - For ethereum:chainId networks: requires EthereumSignRequest fields
    - For solana network: requires SolanaSignRequest fields

    Attributes:
        network: Target network ("ethereum:chainId" or "solana")
        message: Optional short message attached to the transaction
        request: Network-specific transaction details

    Example:
        ```python
        # Ethereum transaction
        await sdk.sign_and_send({
            "network": "ethereum:1",
            "message": "Token transfer",
            "request": {
                "to_address": "0x742d35cc6634C0532925a3b8D65e95f32B6b5582",
                "data": "0xa9059cbb...",  # encoded transfer()
                "value": "0"
            }
        })

        # Solana transaction
        await sdk.sign_and_send({
            "network": "solana",
            "message": "SOL transfer",
            "request": {
                "hex_transaction": "010001030a0b..."
            }
        })
        ```
    """

    network: str = Field(..., description="Target network (ethereum:chainId or solana)")
    message: str | None = Field(
        None,
        description="Optional short message attached to the transaction",
        max_length=250,
    )
    request: EthereumSignRequest | SolanaSignRequest = Field(
        ..., description="Network-specific transaction details"
    )

    @field_validator("network")
    @classmethod
    def validate_network(cls, v: str) -> str:
        """Validate network format."""
        if v == "solana":
            return v
        if v.startswith("ethereum:"):
            try:
                chain_id = int(v.split(":")[1])
                if chain_id <= 0:
                    raise ValueError("Chain ID must be positive")
                return v
            except (IndexError, ValueError):
                raise ValueError(
                    "Invalid ethereum network format. Use ethereum:chainId"
                ) from None
        raise ValueError("Network must be 'solana' or 'ethereum:chainId'")

    @model_validator(mode="after")
    def validate_request_matches_network(self) -> "SignAndSendRequest":
        """Ensure request type matches network."""
        if self.network == "solana":
            if not isinstance(self.request, SolanaSignRequest):
                raise ValueError("Solana network requires SolanaSignRequest")
        elif self.network.startswith("ethereum:"):
            if not isinstance(self.request, EthereumSignRequest):
                raise ValueError("Ethereum network requires EthereumSignRequest")

        return self

    model_config = ConfigDict(extra="forbid")


class EthereumBalanceRequest(BaseModel):
    """Ethereum-specific balance request."""

    token: str | None = Field(
        None,
        description="Optional ERC-20 token address",
        pattern=r"^0x[a-fA-F0-9]{40}$",
    )

    model_config = ConfigDict(extra="forbid")


class SolanaBalanceRequest(BaseModel):
    """Solana-specific balance request."""

    mint: str | None = Field(None, description="Optional SPL token mint address")

    model_config = ConfigDict(extra="forbid")


class GetBalanceRequest(BaseModel):
    """
    Balance request type with network-specific parameters.

    Attributes:
        address: Address to check balance for
        network: Target network
        Additional fields based on network:
        - Ethereum: optional token (ERC-20 contract address)
        - Solana: optional mint (SPL token mint address)

    Example:
        ```python
        # Native balance
        balance = await sdk.utils.get_balance({
            "address": "0x742d35cc6634C0532925a3b8D65e95f32B6b5582",
            "network": "ethereum:1"
        })

        # Token balance
        balance = await sdk.utils.get_balance({
            "address": "0x742d35cc6634C0532925a3b8D65e95f32B6b5582",
            "network": "ethereum:1",
            "token": "0xA0b86a33E6441d9c9C4c5f5b3E6b8e8c0f0f9d1a"
        })
        ```
    """

    address: str = Field(..., description="Address to check balance for")
    network: str = Field(..., description="Target network")
    # Network-specific fields are handled dynamically in validation
    token: str | None = Field(None, description="ERC-20 token address (Ethereum only)")
    mint: str | None = Field(None, description="SPL token mint address (Solana only)")

    @field_validator("network")
    @classmethod
    def validate_network(cls, v: str) -> str:
        """Validate network format."""
        if v == "solana":
            return v
        if v.startswith("ethereum:"):
            try:
                chain_id = int(v.split(":")[1])
                if chain_id <= 0:
                    raise ValueError("Chain ID must be positive")
                return v
            except (IndexError, ValueError):
                raise ValueError("Invalid ethereum network format") from None
        raise ValueError("Network must be 'solana' or 'ethereum:chainId'")

    @model_validator(mode="after")
    def validate_network_specific_fields(self) -> "GetBalanceRequest":
        """Validate that network-specific fields are used correctly."""
        network = self.network
        token = self.token
        mint = self.mint

        if not network:
            return self

        if network == "solana":
            if token is not None:
                raise ValueError(
                    "'token' field not valid for Solana network. Use 'mint' instead."
                )
        elif network.startswith("ethereum:"):
            if mint is not None:
                raise ValueError(
                    "'mint' field not valid for Ethereum network. Use 'token' instead."
                )

        return self

    model_config = ConfigDict(extra="forbid")


class EthereumTransferRequest(BaseModel):
    """Ethereum-specific transfer request."""

    token: str | None = Field(
        None,
        description="Optional ERC-20 token address; omit for native ETH",
        pattern=r"^0x[a-fA-F0-9]{40}$",
    )

    model_config = ConfigDict(extra="forbid")


class SolanaTransferRequest(BaseModel):
    """Solana-specific transfer request."""

    from_address: str = Field(..., description="Source address (required for Solana)")
    mint: str | None = Field(
        None, description="Optional SPL token mint; omit for native SOL"
    )
    decimals: int | None = Field(
        None,
        description="Token decimals (required for SPL tokens when mint provided)",
        ge=0,
    )

    @model_validator(mode="after")
    def validate_decimals_with_mint(self) -> "SolanaTransferRequest":
        """Validate that decimals is provided when mint is specified."""
        if self.mint is not None and self.decimals is None:
            raise ValueError("'decimals' is required when 'mint' is provided")
        return self

    model_config = ConfigDict(extra="forbid")


class TransferRequest(BaseModel):
    """
    Transfer request type with network-specific parameters.

    Usage quick reference:
    - EVM (ethereum:X):
      - Required: to_address, amount (wei as string)
      - Optional: token (ERC-20 address) → token transfer; omit for native
      - Optional: message (short string) → persisted alongside transaction
    - Solana:
      - Required: from_address, to_address, amount
      - Native SOL: omit mint; amount is lamports (1 SOL = 1e9)
      - SPL token: include mint and decimals; amount is in base units

    Example:
        ```python
        # Ethereum native transfer
        await sdk.utils.transfer({
            "network": "ethereum:1",
            "to_address": "0x742d35cc6634C0532925a3b8D65e95f32B6b5582",
            "amount": "1000000000000000000"  # 1 ETH in wei
        })

        # Solana SPL token transfer
        await sdk.utils.transfer({
            "network": "solana",
            "from_address": "9WbZXa5bAz1kMKKJM8jbLbmr6NZrJ3q8JM8jdN9QmQmE",
            "to_address": "8xZXa5bAz1kMKKJM8jbLbmr6NZrJ3q8JM8jdN9QmQmF",
            "amount": "1000000",  # 1 USDC (6 decimals)
            "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            "decimals": 6
        })
        ```
    """

    network: str = Field(..., description="Target network")
    to_address: str = Field(..., description="Recipient address")
    amount: str = Field(..., description="Raw amount as string")
    message: str | None = Field(
        None, description="Optional short message from the agent", max_length=250
    )
    # Network-specific fields
    token: str | None = Field(None, description="ERC-20 token address (Ethereum only)")
    from_address: str | None = Field(
        None, description="Source address (required for Solana)"
    )
    mint: str | None = Field(None, description="SPL token mint address (Solana only)")
    decimals: int | None = Field(
        None, description="Token decimals (Solana SPL tokens only)", ge=0
    )

    @field_validator("network")
    @classmethod
    def validate_network(cls, v: str) -> str:
        """Validate network format."""
        if v == "solana":
            return v
        if v.startswith("ethereum:"):
            try:
                chain_id = int(v.split(":")[1])
                if chain_id <= 0:
                    raise ValueError("Chain ID must be positive")
                return v
            except (IndexError, ValueError):
                raise ValueError("Invalid ethereum network format") from None
        raise ValueError("Network must be 'solana' or 'ethereum:chainId'")

    @model_validator(mode="after")
    def validate_network_requirements(self) -> "TransferRequest":
        """Validate network-specific requirements."""
        if self.network == "solana":
            # Solana requires from_address
            if not self.from_address:
                raise ValueError("'from_address' is required for Solana transfers")

            # If mint is provided, decimals should be too
            if self.mint is not None and self.decimals is None:
                raise ValueError(
                    "'decimals' is required when 'mint' is provided for Solana"
                )

            # Token/mint validation
            if self.token is not None:
                raise ValueError(
                    "'token' field not valid for Solana. Use 'mint' instead."
                )

        elif self.network.startswith("ethereum:"):
            # Ethereum doesn't use these Solana-specific fields
            if self.from_address is not None:
                raise ValueError("'from_address' not used for Ethereum transfers")
            if self.mint is not None:
                raise ValueError(
                    "'mint' field not valid for Ethereum. Use 'token' instead."
                )
            if self.decimals is not None:
                raise ValueError("'decimals' not used for Ethereum transfers")

        return self

    model_config = ConfigDict(extra="forbid")
