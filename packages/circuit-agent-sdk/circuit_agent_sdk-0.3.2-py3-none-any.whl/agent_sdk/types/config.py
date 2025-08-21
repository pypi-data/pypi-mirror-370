"""
Configuration type definitions for the Agent SDK.

This module provides configuration models and constants used throughout the SDK.
"""

from pydantic import BaseModel, ConfigDict, Field

# Base URLs for the API
API_BASE_URL_LOCAL = "https://agents.circuit.org"
# Internal VPC URL for Lambda agents (resolves to proxy instance)
API_BASE_URL_LAMBDA = "http://transaction-service.agent.internal"


class SDKConnections(BaseModel):
    """
    User-provided RPC connections configuration.

    This model defines the RPC endpoints used by the SDK utilities for
    blockchain operations that require direct chain access.

    Attributes:
        evm: Mapping of chain ID to RPC URL for EVM-compatible chains
        solana: Single RPC URL for Solana network

    Example:
        ```python
        connections = SDKConnections(
            evm={
                1: "https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY",
                42161: "https://arb-mainnet.g.alchemy.com/v2/YOUR_KEY"
            },
            solana="https://api.mainnet-beta.solana.com"
        )
        ```
    """

    evm: dict[int, str] | None = Field(
        None, description="Mapping of chain ID to RPC URL for EVM networks"
    )
    solana: str | None = Field(None, description="RPC URL for Solana network")

    model_config = ConfigDict(extra="forbid")


class SDKConfig(BaseModel):
    """
    Configuration for the SDK client.

    This is the main configuration object passed to AgentSdk constructor.
    Only sessionId is required; all other fields have sensible defaults.

    Attributes:
        session_id: Numeric session identifier that scopes auth and actions
        verbose: Enable verbose logging for debugging requests/responses
        testing: Enable testing mode to return mock responses instead of real calls
        base_url: Override API base URL (auto-detected if not provided)
        connections: Optional RPC URLs used by utils for direct chain access

    Example:
        ```python
        # Minimal configuration
        config = SDKConfig(session_id=123)

        # Full configuration
        config = SDKConfig(
            session_id=123,
            verbose=True,
            testing=False,
            base_url="https://custom-api.example.com"
        )
        ```
    """

    session_id: int = Field(
        ...,
        description="Session ID for the current agent instance",
        gt=0,  # Must be positive
    )
    verbose: bool = Field(False, description="Enable verbose logging for debugging")
    testing: bool = Field(
        False, description="Enable testing mode to return mock responses"
    )
    base_url: str | None = Field(None, description="Optional base URL for API requests")
    # connections: SDKConnections | None = Field(
    #     None, description="Optional RPC connections config for utilities"
    # )

    model_config = ConfigDict(extra="forbid")
