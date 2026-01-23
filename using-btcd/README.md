# P2P Todo - Decentralized Task Manager

Ứng dụng quản lý Todo phi tập trung. Chạy trên LAN, không server, tự động sync giữa các máy.

## Quick Start

```bash
# Build
go build -o p2p-todo.exe

# Run
./p2p-todo.exe
```

## Commands

| Command | Description |
|---------|-------------|
| `add <title>` | Thêm todo mới |
| `list` | Xem tất cả todos |
| `done <id>` | Đánh dấu hoàn thành |
| `delete <id>` | Xóa todo |
| `peers` | Xem số peers đã kết nối |
| `sync` | Force sync với peers |
| `quit` | Thoát |

## How It Works

1. **P2P Network**: Dùng libp2p + GossipSub để gửi/nhận messages
2. **Auto-Discovery**: mDNS tự động tìm peers trên LAN
3. **CRDT Sync**: LWW-Map đảm bảo data consistency
4. **Persistence**: Data lưu tại `~/.p2p-todo/todos.json`

## Multi-Machine Usage

1. Chạy app trên Machine A: `./p2p-todo.exe`
2. Chạy app trên Machine B (cùng LAN): `./p2p-todo.exe`
3. Các máy tự động phát hiện và sync data
