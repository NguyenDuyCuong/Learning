# Product Vision: P2P Todo

## Why this project exists
To provide a private, serverless, and resilient way to manage tasks. Traditional todo apps rely on central servers which can be a single point of failure and raise privacy concerns. P2P Todo empowers users to own their data and sync it directly between their own devices or within a trusted group.

## Problems it solves
- **Centralization**: Removes dependency on a central service provider.
- **Privacy**: Data is only shared with connected peers, not stored on some company's server.
- **Availability**: Works on local networks even without internet access.
- **Complexity**: Provides a single binary solution that is easy to deploy and run.

## Target Users
- Users who value privacy and data ownership.
- Teams working on the same local network (e.g., in an office or at a hackathon).
- Developers interested in decentralized systems and CRDTs.

## How it works (High-level)
1. **Peers**: Each user runs a node.
2. **Discovery**: Nodes find each other on the LAN (mDNS) or through a DHT on the internet.
3. **Data Sync**: When nodes connect, they exchange their task records.
4. **Consistency**: CRDT logic handles concurrent edits (e.g., two people completing the same task).
5. **UI**: A CLI provides a familiar interface for managing the task list.

## User Experience Goals
- **Instant sync**: Changes should propagate to connected peers as quickly as possible.
- **Conflict-free**: Users should never have to manually resolve merge conflicts.
- **Transparency**: Clear feedback on connection status and synchronization progress.

## Success Metrics
- Successful synchronization between at least two nodes on a LAN.
- Reliable persistence of data across restarts.
- Handling of edge cases like offline deletions (via Tombstones).
