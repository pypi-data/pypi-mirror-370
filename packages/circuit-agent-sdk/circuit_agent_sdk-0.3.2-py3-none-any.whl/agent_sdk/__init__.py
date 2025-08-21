"""
Circuit Agent Python SDK — clean, type-safe agent automation.

- `AgentSdk` — main class with `add_message()` and `sign_and_send()`
- `AgentUtils` — utilities available via `AgentSdk(...).utils`
- Types & guards — networks, requests, responses

Install: `pip install circuit-agent-sdk`

Minimal example:
```python
from agent_sdk import AgentSdk, SDKConfig

sdk = AgentSdk(SDKConfig(session_id=123))
await sdk.add_message({"type": "observe", "short_message": "Hello"})
```

Features:
- 🎯 Simple API: Only 2 main methods - `add_message()` and `sign_and_send()`
- 🔒 Type Safety: Network parameter determines valid request shapes automatically
- 🚀 Cross-Chain: Unified interface for EVM and Solana networks
- 📦 Utilities: Helper functions for common operations
- 🛠️ HTTP Server: Agent wrapper for local/worker deployment

For more information, see the README.md file or visit:
https://github.com/circuitorg/agent-sdk-python
"""

# Main SDK exports
# Agent wrapper for local/worker deployment
from .agent import (
    Agent,
    AgentConfig,
    AgentRequest,
    AgentResponse,
    ChatFunctionContract,
    ExecutionFunctionContract,
    HealthCheckFunctionContract,
    HealthResponse,
    StopFunctionContract,
    create_agent_handler,
)
from .agent_sdk import AgentSdk

# Core types
from .types import (
    AddMessageRequest,
    BalanceResponse,
    GetBalanceRequest,
    Network,
    SDKConfig,
    SDKConnections,
    SignAndSendRequest,
    SignAndSendResponse,
    TransferRequest,
    get_chain_id_from_network,
    is_ethereum_network,
    is_solana_network,
)

# Utility functions
from .utils import get_agent_config_from_pyproject, setup_logging

__version__ = "0.2.0"
__author__ = "Circuit Team"
__email__ = "team@circuit.org"
__description__ = (
    "Circuit Agent Python SDK - Clean, type-safe agent automation for Circuit"
)

__all__ = [
    # Main SDK
    "AgentSdk",
    # Agent wrapper for HTTP server deployment
    "Agent",
    "AgentConfig",
    "AgentRequest",
    "AgentResponse",
    "HealthResponse",
    "create_agent_handler",
    "ExecutionFunctionContract",
    "StopFunctionContract",
    "ChatFunctionContract",
    "HealthCheckFunctionContract",
    # Core types
    "Network",
    "SDKConfig",
    "SDKConnections",
    "AddMessageRequest",
    "SignAndSendRequest",
    "SignAndSendResponse",
    "GetBalanceRequest",
    "TransferRequest",
    "BalanceResponse",
    # Network detection utilities
    "is_ethereum_network",
    "is_solana_network",
    "get_chain_id_from_network",
    # Utility functions
    "get_agent_config_from_pyproject",
    "setup_logging",
]
