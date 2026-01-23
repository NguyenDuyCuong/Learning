package main

import (
	"bufio"
	"context"
	"encoding/json"
	"fmt"
	"os"
	"os/signal"
	"path/filepath"
	"sort"
	"strings"
	"syscall"

	"p2p-todo/crdt"
	"p2p-todo/p2p"
	"p2p-todo/todo"
)

func main() {
	fmt.Println("╔══════════════════════════════════════╗")
	fmt.Println("║   P2P Todo - Decentralized Tasks     ║")
	fmt.Println("╚══════════════════════════════════════╝")
	fmt.Println()

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// Setup data directory
	dataDir := getDataDir()
	os.MkdirAll(dataDir, 0755)

	// Create CRDT store
	storePath := filepath.Join(dataDir, "todos.json")
	store := crdt.NewStore(storePath)
	fmt.Printf("📁 Data: %s\n", storePath)

	// Create P2P node
	fmt.Println("🔄 Starting P2P node...")
	fmt.Println("🌐 Hybrid Mode: LAN (mDNS) + Internet (DHT/Relay) active")
	node, err := p2p.NewNode(ctx, dataDir)
	if err != nil {
		fmt.Printf("❌ Failed to start node: %v\n", err)
		os.Exit(1)
	}
	defer node.Close()

	fmt.Printf("🆔 Peer ID: %s\n", node.PeerID[:16]+"...")
	fmt.Println("📡 Listening on:")
	for _, addr := range node.Addresses() {
		fmt.Printf("   %s\n", addr)
	}
	fmt.Println("📡 Discovering peers on LAN...")

	// Create todo manager
	manager := todo.NewManager(store, node.PeerID)

	// Helper to broadcast full state
	broadcastState := func() {
		state := store.GetState()
		data, _ := json.Marshal(state)
		node.Broadcast(p2p.MsgSync, data)
		fmt.Printf("📤 Sent %d todos to peers\n> ", len(state))
	}

	// Setup message handler for sync
	node.OnMessage = func(data []byte) {
		var msg p2p.Message
		if err := json.Unmarshal(data, &msg); err != nil {
			return
		}

		switch msg.Type {
		case p2p.MsgSyncRequest:
			// Peer is requesting our state - send it
			fmt.Printf("\n📥 Sync request from %s\n", msg.From[:8])
			broadcastState()

		case p2p.MsgSync:
			// Receive full state from peer
			var todos []*crdt.Todo
			if err := json.Unmarshal(msg.Payload, &todos); err != nil {
				return
			}
			merged := store.Merge(todos)
			if merged > 0 {
				fmt.Printf("\n⬇️  Synced %d todos from %s\n> ", merged, msg.From[:8])
			}

		case p2p.MsgUpdate:
			// Receive single todo update
			var t crdt.Todo
			if err := json.Unmarshal(msg.Payload, &t); err != nil {
				return
			}
			if store.Add(&t) {
				status := "[ ]"
				if t.Done {
					status = "[✓]"
				}
				fmt.Printf("\n⬇️  New: %s %s (%s)\n> ", status, t.Title, t.ID[:6])
			}
		}
	}

	// When new peer connects, broadcast our state AND request theirs
	node.OnPeerConnected = func() {
		fmt.Printf("\n🔗 New peer connected! Syncing...\n")
		// Send our state to the new peer
		broadcastState()
		// Request their state too
		node.RequestSync()
	}

	// Handle shutdown
	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, syscall.SIGINT, syscall.SIGTERM)
	go func() {
		<-sigCh
		fmt.Println("\n👋 Shutting down...")
		cancel()
		os.Exit(0)
	}()

	// CLI loop
	fmt.Println()
	fmt.Println("Commands: add <title> | list | done <id> | delete <id> | peers | quit")
	fmt.Println()

	scanner := bufio.NewScanner(os.Stdin)
	for {
		fmt.Print("> ")
		if !scanner.Scan() {
			break
		}

		line := strings.TrimSpace(scanner.Text())
		if line == "" {
			continue
		}

		parts := strings.SplitN(line, " ", 2)
		cmd := strings.ToLower(parts[0])

		switch cmd {
		case "add":
			if len(parts) < 2 {
				fmt.Println("Usage: add <title>")
				continue
			}
			t := manager.Add(parts[1])
			fmt.Printf("✅ Added: %s (ID: %s)\n", t.Title, t.ID)

			// Broadcast the new todo
			data, _ := json.Marshal(t)
			node.Broadcast(p2p.MsgUpdate, data)

		case "list", "ls":
			todos := manager.List()
			if len(todos) == 0 {
				fmt.Println("📋 No todos yet. Use 'add <title>' to create one.")
				continue
			}

			// Sort by timestamp
			sort.Slice(todos, func(i, j int) bool {
				return todos[i].Timestamp < todos[j].Timestamp
			})

			fmt.Println()
			fmt.Println("📋 Todos:")
			for _, t := range todos {
				status := "[ ]"
				if t.Done {
					status = "[✓]"
				}
				author := t.Author[:8]
				if t.Author == node.PeerID {
					author = "you"
				}
				fmt.Printf("  %s %s - %s (by %s)\n", status, t.ID[:6], t.Title, author)
			}
			fmt.Println()

		case "done":
			if len(parts) < 2 {
				fmt.Println("Usage: done <id>")
				continue
			}
			id := findTodoID(manager.List(), parts[1])
			if id == "" {
				fmt.Println("❌ Todo not found")
				continue
			}
			if t := manager.MarkDone(id); t != nil {
				fmt.Println("✅ Marked as done")
				// Broadcast the update
				data, _ := json.Marshal(t)
				node.Broadcast(p2p.MsgUpdate, data)
			}

		case "delete", "del", "rm":
			if len(parts) < 2 {
				fmt.Println("Usage: delete <id>")
				continue
			}
			id := findTodoID(manager.List(), parts[1])
			if id == "" {
				fmt.Println("❌ Todo not found")
				continue
			}
			manager.Delete(id)
			fmt.Println("🗑️  Deleted")

		case "peers":
			fmt.Printf("👥 Connected peers: %d\n", node.PeerCount())
			fmt.Println("📡 Your Addresses:")
			for _, addr := range node.Addresses() {
				fmt.Printf("   %s\n", addr)
			}

		case "connect":
			if len(parts) < 2 {
				fmt.Println("Usage: connect <multiaddress>")
				continue
			}
			addr := parts[1]
			fmt.Printf("🔗 Connecting to %s...\n", addr)
			if err := node.Connect(addr); err != nil {
				fmt.Printf("❌ Connection failed: %v\n", err)
			} else {
				fmt.Println("✓ Connected successfully!")
			}

		case "sync":
			state := store.GetState()
			data, _ := json.Marshal(state)
			node.Broadcast(p2p.MsgSync, data)
			fmt.Printf("📤 Broadcasted %d todos\n", len(state))

		case "quit", "exit", "q":
			fmt.Println("👋 Bye!")
			return

		case "help", "?":
			fmt.Println("Commands:")
			fmt.Println("  add <title>  - Add a new todo")
			fmt.Println("  list         - List all todos")
			fmt.Println("  done <id>    - Mark todo as done")
			fmt.Println("  delete <id>  - Delete a todo")
			fmt.Println("  peers        - Show connected peers")
			fmt.Println("  sync         - Force sync with peers")
			fmt.Println("  quit         - Exit")

		default:
			fmt.Println("Unknown command. Type 'help' for commands.")
		}
	}
}

// findTodoID finds a todo by partial ID match
func findTodoID(todos []*crdt.Todo, partial string) string {
	partial = strings.ToLower(partial)
	for _, t := range todos {
		if strings.HasPrefix(strings.ToLower(t.ID), partial) {
			return t.ID
		}
	}
	return ""
}

// getDataDir returns the data directory path
func getDataDir() string {
	home, _ := os.UserHomeDir()
	return filepath.Join(home, ".p2p-todo")
}
