# Tech Stack: P2P Todo

## Languages
- **Go (Golang)**: Core implementation language.

## Frameworks & Major Libraries
- **libp2p**: Core P2P networking library.
    - `go-libp2p-kad-dht`: DHT for peer discovery.
    - `go-libp2p-pubsub`: GossipSub for message broadcasting.
    - `go-libp2p/p2p/net/connmgr`: Connection management.
- **CRDT**: Custom implementation of LWW-Map.

## Development Tools
- **Go Modules**: Dependency management.
- **PowerShell/Bash**: Build scripts and environment management.

## Technical Constraints
- **Multi-platform support**: Must work on Windows and Linux.
- **Network conditions**: Must handle NAT traversal and varying network reliability.
- **Performance**: Low memory footprint and efficient synchronization.

## Testing Frameworks
- **Go testing**: Built-in `testing` package for unit tests.

## Deployment Environment
- **Single Binary**: The application is compiled into a standalone binary for distribution.
- **User Home Directory**: Config and data stored in `~/.p2p-todo/`.

## External Services/APIs
- **Bootstrap Nodes**: Public libp2p bootstrap nodes for initial WAN discovery.
- **Relay Nodes**: Public relays for NAT traversal when hole punching fails.
