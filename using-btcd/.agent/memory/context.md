# Context: P2P Todo

## Current Work Focus
- Initializing the Project Memory Bank to improve AI understanding of the project.
- Debugging P2P bootstrapping issues (as mentioned in conversation history).
- Refactoring CRDT implementation to support Tombstone-based deletions.

## Recent Significant Changes
- Added Peer ID persistence to `~/.p2p-todo/priv.key`.
- Enabled Hybrid mode (LAN + Internet) with AutoRelay and Hole Punching.
- Fixed bootstrap Peer ID mismatch issues.
- Integrated CRDT LWW-Map for basic synchronization.

## Next Planned Steps
- Finish Memory Bank initialization.
- Implement more robust error handling for connection failures (UDP buffer warnings, etc.).
- Enhance CLI with better connection status visualization.
- Complete the transition to tombstone-based deletions in `crdt/store.go`.

## Active Branches/Features
- `main`: Primary development branch.
- Feature: Tombstone-based deletion (in progress).
- Feature: Internet discovery via DHT/Relay (implemented, being refined).
