# unrealon-rpc

Universal async RPC + mesh + storage over Redis and IPFS with FastAPI WebSocket support.

## Features

- **Generic WebSocket Bridge**: Universal WebSocket-to-Redis communication layer
- **Parser-Specific Bridge**: Domain-specific wrapper for parser orchestration
- **Redis RPC/PubSub**: Asynchronous messaging primitives
- **IPFS Storage**: Decentralized file storage integration
- **Pydantic v2**: Strict type validation and data modeling
- **Modular Architecture**: Clean separation of concerns with dependency injection

## Installation

```bash
pip install unrealon-rpc
```

## Quick Start

### Start WebSocket Server

```bash
# Production mode
ws-server --host localhost --port 8000

# Development mode with auto-reload (port 8001)
ws-dev --host localhost --port 8001
```

### Start Parser Bridge Server

```bash
# Production mode
parser-bridge --redis-url redis://localhost:6379/0

# Development mode with auto-reload (port 8002)
parser-dev --redis-url redis://localhost:6379/0
```

### Python Usage

```python
from bridge_parsers import ParserBridgeServer, ParserBridgeClient

# Server
server = ParserBridgeServer(redis_url="redis://localhost:6379/0")
await server.start()

# Client
client = ParserBridgeClient(
    websocket_url="ws://localhost:8000/ws",
    parser_type="my_parser"
)
await client.connect()
```

## Architecture

The system follows a clean architecture with:

- **Generic Bridge** (`unrealon_rpc.bridge`): WebSocket-to-Redis communication
- **Parser Bridge** (`bridge_parsers`): Domain-specific parser orchestration
- **RPC Layer** (`unrealon_rpc.rpc`): Redis-based RPC implementation
- **PubSub Layer** (`unrealon_rpc.pubsub`): Redis-based publish/subscribe

## Testing

```bash
# Run all tests
python tests/run_tests.py

# Run specific test types
python tests/run_tests.py --type unit
python tests/run_tests.py --type e2e
```

## Documentation

See the `@docs/` directory for comprehensive documentation.

## License

MIT License
