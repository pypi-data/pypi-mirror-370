"""
Main AgentSdk class with simplified API surface.

This module provides the primary AgentSdk class that serves as the main entry point
for all agent operations. It offers a clean, type-safe interface with just two
core methods that cover the majority of agent interactions.
"""

from typing import Any

from .client import APIClient
from .types import (
    AddMessageRequest,
    SDKConfig,
    SignAndSendRequest,
    SignAndSendResponse,
    get_chain_id_from_network,
    is_ethereum_network,
    is_solana_network,
)
from .types.requests import EthereumSignRequest, SolanaSignRequest


class AgentSdk:
    """
    Main SDK entrypoint used by agents to interact with the Circuit backend.

    Provides a minimal, type-safe surface with two core methods that cover the
    majority of agent interactions:

    - add_message() — emit timeline messages for observability and UX
    - sign_and_send() — sign and broadcast transactions across networks

    Quick start:
        ```python
        from agent_sdk import AgentSdk, SDKConfig

        sdk = AgentSdk(SDKConfig(
            session_id=request.session_id,
        ))

        await sdk.add_message({
            "type": "observe",
            "short_message": "Starting"
        })

        tx = await sdk.sign_and_send({
            "network": "ethereum:42161",
            "request": {
                "to_address": "0xabc...",
                "data": "0x",
                "value": "0"
            },
            "message": "Funding user"
        })
        ```
    """

    def __init__(self, config: SDKConfig) -> None:
        """
        Create a new AgentSdk instance.

        Args:
            config: SDK configuration
                - session_id: Numeric session identifier that scopes auth and actions
                - verbose: When True, prints detailed request/response logs
                - testing: When True, short-circuits network calls with mock values
                - base_url: Override API base URL (detected automatically otherwise)

        Example:
            ```python
            sdk = AgentSdk(SDKConfig(session_id=42, verbose=True))
            ```
        """
        self.config = config
        self.client = APIClient(config)
        # Pass the sign_and_send method to utils to avoid circular dependency
        # self.utils = AgentUtils(self.client, self.config, self.sign_and_send)

    def _log(self, message: str, data: Any = None) -> None:
        """Log debug information when verbose mode is enabled."""
        if self.config.verbose:
            log_message = f"[AGENT SDK DEBUG] {message}"
            if data is not None:
                import json

                log_message += f" {json.dumps(data, indent=2, default=str)}"
            print(log_message)

    async def add_message(self, message: AddMessageRequest | dict) -> None:
        """
        Add a message to the agent timeline.

        Messages show up in session traces and UIs and are useful for observability,
        human-in-the-loop reviews, and debugging.

        Args:
            message: Timeline message with the following fields:
                - type: Message type for categorization. Options:
                    • "observe"  - General observations and status updates
                    • "validate" - Validation checks and confirmations
                    • "reflect"  - Analysis and reasoning about actions
                    • "error"    - Error messages and failures
                    • "warning"  - Warnings and potential issues
                - short_message: Brief, human-readable message (automatically truncated to 250 characters if longer)

        Raises:
            requests.RequestException: If the backend request fails

        Examples:
            ```python
            # Status observation
            await sdk.add_message({
                "type": "observe",
                "short_message": "Starting swap operation"
            })
            # Validation check
            await sdk.add_message({
                "type": "validate",
                "short_message": "Confirmed sufficient balance: 1.5 ETH"
            })
            # Error reporting
            await sdk.add_message({
                "type": "error",
                "short_message": "Transaction failed: insufficient gas"
            })
            # Long messages are automatically truncated to 250 characters (when using dict input)
            await sdk.add_message({
                "type": "observe",
                "short_message": "This is a very long message that will be automatically truncated if it exceeds 250 characters to prevent validation failures and ensure the message gets through successfully"
            })
            # Note: Pydantic models must be valid when created (max 250 chars)
            # Dict inputs are automatically truncated by the SDK
            ```
        """
        # Handle both dict and Pydantic model inputs (like TypeScript SDK)
        if isinstance(message, dict):
            # Automatically truncate messages that exceed 250 characters before validation
            if "short_message" in message and len(message["short_message"]) > 250:
                original_message = message["short_message"]
                truncated_message = original_message[:247] + "..."
                self._log(
                    f"Message truncated from {len(original_message)} to 250 characters"
                )
                message["short_message"] = truncated_message

            # Convert dict to Pydantic model for validation and type safety
            message_obj = AddMessageRequest(**message)
        else:
            # For Pydantic models, we need to handle truncation differently
            # since validation already happened. We'll create a new dict and truncate it.
            message_dict = message.model_dump()

            if len(message_dict["short_message"]) > 250:
                original_message = message_dict["short_message"]
                truncated_message = original_message[:247] + "..."
                self._log(
                    f"Message truncated from {len(original_message)} to 250 characters"
                )
                message_dict["short_message"] = truncated_message
                # Create a new Pydantic model with the truncated message
                message_obj = AddMessageRequest(**message_dict)
            else:
                message_obj = message

        self._log("=== ADD MESSAGE ===")
        self._log("Message:", message_obj.model_dump())
        self._log("===================")

        # Convert to the internal messages format
        messages_request = [
            {"type": message_obj.type, "shortMessage": message_obj.short_message}
        ]

        await self._message_send(messages_request)

    async def sign_and_send(
        self, request: SignAndSendRequest | dict
    ) -> SignAndSendResponse:
        """
        Sign and broadcast a transaction on the specified network.

        The backend performs validation and policy checks; you only need to provide
        the minimal request shape for the selected network.

        Args:
            request: Network-specific transaction input
                - network: "solana" or "ethereum:chainId"
                - message: Optional human-readable context message (short), stored with the transaction
                - request: Transaction payload
                  - For Ethereum: {"to_address": "0x...", "data": "0x...", "value": "wei_amount"}
                    - to_address: recipient contract or EOA as hex string
                    - data: calldata as hex string (use "0x" for simple transfers)
                    - value: stringified wei amount
                  - For Solana: {"hex_transaction": "hex_string"}
                    - hex_transaction: serialized VersionedTransaction as hex string

        Returns:
            SignAndSendResponse with internal_transaction_id, tx_hash, and optional transaction_url

        Raises:
            ValueError: If the network is unsupported or request validation fails
            requests.RequestException: If the backend rejects the request

        Example:
            ```python
            # Ethereum (Arbitrum) native transfer
            await sdk.sign_and_send({
                "network": "ethereum:42161",
                "request": {
                    "to_address": "0xabc...",
                    "data": "0x",
                    "value": "1000000000000000"  # 0.001 ETH
                },
                "message": "Self-transfer demo"
            })

            # Solana
            await sdk.sign_and_send({
                "network": "solana",
                "request": {"hex_transaction": "01ab..."},
                "message": "Swap with Jupiter"
            })
            ```
        """
        # Handle both dict and Pydantic model inputs (like TypeScript SDK)
        if isinstance(request, dict):
            # Convert dict to Pydantic model for validation and type safety
            request_obj = SignAndSendRequest(**request)
        else:
            request_obj = request
        self._log("=== SIGN AND SEND ===")
        self._log("Request:", request_obj.model_dump())
        self._log("Testing mode:", self.config.testing)
        self._log("====================")

        if self.config.testing:
            return SignAndSendResponse(
                internal_transaction_id=123,
                tx_hash=(
                    "0xTEST"
                    if is_ethereum_network(request_obj.network)
                    else "TEST_SOL_TX"
                ),
                transaction_url=None,
            )

        if is_ethereum_network(request_obj.network):
            chain_id = get_chain_id_from_network(request_obj.network)

            # Ensure we have an Ethereum request
            if not isinstance(request_obj.request, EthereumSignRequest):
                raise ValueError("Ethereum network requires EthereumSignRequest")

            return await self._handle_evm_transaction(
                {
                    "chainId": chain_id,
                    "toAddress": request_obj.request.to_address,
                    "data": request_obj.request.data,
                    "valueWei": request_obj.request.value,  # Map 'value' to 'valueWei'
                    "message": request_obj.message,
                }
            )

        if is_solana_network(request_obj.network):
            # Ensure we have a Solana request
            if not isinstance(request_obj.request, SolanaSignRequest):
                raise ValueError("Solana network requires SolanaSignRequest")

            return await self._handle_solana_transaction(
                {
                    "hexTransaction": request_obj.request.hex_transaction,
                    "message": request_obj.message,
                }
            )

        raise ValueError(f"Unsupported network: {request_obj.network}")

    # =====================
    # Private Implementation Methods (migrated from AgentToolset)
    # =====================

    async def _handle_evm_transaction(
        self, request: dict[str, Any]
    ) -> SignAndSendResponse:
        """Handle EVM transaction signing and broadcasting."""
        # 1) Sign the transaction
        sign_response = self.client.post("/v1/transactions/evm", request)

        # 2) Broadcast the transaction
        transaction_id = sign_response["internalTransactionId"]
        broadcast_response = self.client.post(
            f"/v1/transactions/evm/{transaction_id}/broadcast"
        )

        return SignAndSendResponse(
            internal_transaction_id=transaction_id,
            tx_hash=broadcast_response["txHash"],
            transaction_url=broadcast_response.get("transactionUrl"),
        )

    async def _handle_solana_transaction(
        self, request: dict[str, Any]
    ) -> SignAndSendResponse:
        """Handle Solana transaction signing and broadcasting."""
        # 1) Sign the transaction
        sign_response = self.client.post("/v1/transactions/solana", request)

        # 2) Broadcast the transaction
        transaction_id = sign_response["internalTransactionId"]
        broadcast_response = self.client.post(
            f"/v1/transactions/solana/{transaction_id}/broadcast"
        )

        return SignAndSendResponse(
            internal_transaction_id=transaction_id,
            tx_hash=broadcast_response["txHash"],
            transaction_url=broadcast_response.get("transactionUrl"),
        )

    async def _message_send(self, messages: list) -> dict[str, Any]:
        """Send messages to the agent timeline (migrated from AgentToolset)."""
        if self.config.testing:
            print(f"Messages added successfully (TESTING): {messages}")
            return {
                "status": 200,
                "message": "Messages added successfully (TESTING)",
            }

        return self.client.post("/v1/messages", messages)

    # No legacy methods - clean major version!
