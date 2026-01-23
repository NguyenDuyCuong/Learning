# CONTINUITY.md

## Goal (incl. success criteria)
Tạo decentralized Todo/Task management app hỗ trợ LAN (mDNS) và Internet (DHT/Relay/Manual Connect).

**Success criteria:**
- Single binary Go app, không server trung tâm
- Auto-discovery peers bằng mDNS (LAN) và DHT (WAN)
- Lệnh `connect <addr>` cho phép join từ Internet qua Multiaddress
- Peer ID persistence lưu tại `.p2p-todo/priv.key`
- Data sync đồng nhất qua CRDT LWW-Map (với Tombstones cho deletion)
- Reliable bootstrapping (không treo lâu khi node chết)

## Constraints/Assumptions
- Hỗ trợ cả Offline LAN và Online Internet
- Tự động vượt NAT (UPnP, Hole Punching, Relay)
- libp2p networking (Noise, TLS, QUIC, TCP)
- CRDT cho data consistency (LWW-Map)

## Key decisions
- ✅ Identity: Persistent Peer IDs (Ed25519)
- ✅ Discovery: mDNS + DHT Dual mode
- ✅ Connectivity: AutoRelay + Hole Punching (DCUtR) enabled
- ✅ Interface: CLI với lệnh sync và connect thủ công
- 🛠️ Data: Switching to Tombstone-based deletion for true CRDT behavior

## State
### Done
- Peer ID Persistence
- AutoRelay, DHT, QUIC và Hole Punching
- Hybrid mode (LAN + Internet)
- Fixed bootstrap Peer ID mismatch

### Now
- Cleaning up bootstrap nodes to remove unreliable entries.
- Refactoring `crdt/store.go` to support Tombstones for deletions.
- Improving error handling across the codebase.
- Code review and cleanup.

### Next
- Implement user-friendly connection status in CLI.
- (Optional) Better conflict resolution messages.

## Open questions
- (none)

## Working set
- `p2p/node.go`: Advanced networking & persistence
- `main.go`: CLI commands for connect/peers
- `crdt/store.go`: Data consistency
