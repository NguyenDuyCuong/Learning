# CONTINUITY.md

## Goal (incl. success criteria)
Tạo decentralized Todo/Task management app hỗ trợ LAN (mDNS) và Internet (DHT/Relay/Manual Connect).

**Success criteria:**
- Single binary Go app, không server trung tâm
- Auto-discovery peers bằng mDNS (LAN) và DHT (WAN)
- Lệnh `connect <addr>` cho phép join từ Internet qua Multiaddress
- Peer ID persistence lưu tại `.p2p-todo/priv.key`
- Data sync đồng nhất qua CRDT LWW-Map

## Constraints/Assumptions
- Hỗ trợ cả Offline LAN và Online Internet
- Tự động vượt NAT (UPnP, Hole Punching, Relay)
- libp2p networking (Noise, TLS, QUIC, TCP)
- CRDT cho data consistency

## Key decisions
- ✅ Identity: Persistent Peer IDs (Ed25519)
- ✅ Discovery: mDNS + DHT Dual mode
- ✅ Connectivity: AutoRelay + Hole Punching (DCUtR) enabled
- ✅ Interface: CLI với lệnh sync và connect thủ công

## State
### Done
- Peer ID Persistence (sửa lỗi "message too short" do self-dial)
- Thêm lệnh `connect <multiaddress>`
- Cấu hình AutoRelay, DHT, QUIC và Hole Punching
- Khử trùng lặp local address trong peer discovery
- Build binary thành công (p2p-todo.exe, p2p-todo-linux)
- Đã sửa lỗi panic AutoRelay bằng cách cung cấp PeerSource
- Triển khai chế độ Hybrid (LAN + Internet tự động)
- Sử dụng Public Bootstrap Nodes và Circuit Relays (Protocol Labs)

### Now
- P2P Bootstrapping fixed (Connected to bootstrap nodes).
- Mode Hybrid (LAN + Internet) fully functional.

### Next
- (Optional) Add bootstrap nodes for easier internet discovery

## Open questions
- (none)

## Working set
- `p2p/node.go`: Advanced networking & persistence
- `main.go`: CLI commands for connect/peers
- `crdt/store.go`: Data consistency
