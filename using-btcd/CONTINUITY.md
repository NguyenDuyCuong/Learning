# CONTINUITY.md

## Goal (incl. success criteria)
Tạo decentralized Todo/Task management app sử dụng libp2p + CRDT, chạy trên LAN không internet.

**Success criteria:**
- Single binary Go app, không server
- Auto-discovery peers bằng mDNS
- Data sync và đồng nhất qua CRDT
- Multi-node consistency đảm bảo

## Constraints/Assumptions
- Không có internet - chạy hoàn toàn offline trên LAN
- Không có server - mỗi client tự join mạng
- libp2p cho P2P networking
- CRDT cho data consistency

## Key decisions
- ✅ Architecture: libp2p + CRDT (thay vì btcd)
- ✅ Client language: Go
- ✅ Feature: Todo/Task management
- ✅ Consistency: CRDT ensures eventual consistency

## State
### Done
- Architecture review và decision
- Created P2P node với libp2p + mDNS + GossipSub
- Created CRDT LWW-Map store
- Created Todo manager và CLI
- Fixed handshake issue: explicitly added Noise and TLS security transports
- Improved UI: display listening addresses for debugging
- Build thành công (p2p-todo.exe - 37MB)

### Now
- ✅ Handshake fix complete - ready for re-test

### Next
- User tests on 2 machines again

## Open questions
- (none)

## Working set
- Workspace: `c:\Users\cuong\workspace\Learning\using-btcd`
- Tech: go-libp2p, mDNS, CRDT
