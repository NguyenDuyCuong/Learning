package p2p

import (
	"context"
	"crypto/rand"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"sync"
	"time"

	"github.com/libp2p/go-libp2p"
	dht "github.com/libp2p/go-libp2p-kad-dht"
	pubsub "github.com/libp2p/go-libp2p-pubsub"
	"github.com/libp2p/go-libp2p/core/crypto"
	"github.com/libp2p/go-libp2p/core/host"
	"github.com/libp2p/go-libp2p/core/peer"
	"github.com/libp2p/go-libp2p/p2p/discovery/mdns"
	libp2pnoise "github.com/libp2p/go-libp2p/p2p/security/noise"
	libp2ptls "github.com/libp2p/go-libp2p/p2p/security/tls"
	"github.com/multiformats/go-multiaddr"
)

const (
	// Topic name for todo sync
	TodoTopic = "p2p-todo-sync"
	// mDNS service tag
	ServiceTag = "p2p-todo-mdns"
)

// Node represents a P2P node
type Node struct {
	ctx             context.Context
	Host            host.Host
	PubSub          *pubsub.PubSub
	Topic           *pubsub.Topic
	Sub             *pubsub.Subscription
	DHT             *dht.IpfsDHT
	PeerID          string
	OnMessage       func([]byte) // callback when message received
	OnPeerConnected func()       // callback when new peer connects
	mu              sync.RWMutex
	peers           map[peer.ID]struct{}
}

// Message types
type MessageType string

const (
	MsgSync        MessageType = "sync"         // Full state sync (response)
	MsgUpdate      MessageType = "update"       // Single todo update
	MsgSyncRequest MessageType = "sync_request" // Request full state from peers
)

// Message wraps data sent over pubsub
type Message struct {
	Type    MessageType `json:"type"`
	From    string      `json:"from"`
	Payload []byte      `json:"payload"`
}

// NewNode creates a new P2P node
func NewNode(ctx context.Context, dataDir string) (*Node, error) {
	// 1. Load or generate identity key
	priv, err := loadOrGenerateKey(dataDir)
	if err != nil {
		return nil, fmt.Errorf("failed to load identity: %w", err)
	}

	// 2. Create libp2p host with advanced features
	h, err := libp2p.New(
		libp2p.Identity(priv),
		libp2p.ListenAddrStrings(
			"/ip4/0.0.0.0/tcp/0",      // Random TCP port
			"/ip4/0.0.0.0/udp/0/quic", // Random QUIC port
		),
		// Security
		libp2p.Security(libp2pnoise.ID, libp2pnoise.New),
		libp2p.Security(libp2ptls.ID, libp2ptls.New),
		// NAT Traversal & Relay
		libp2p.NATPortMap(),
		libp2p.EnableAutoRelay(),
		libp2p.EnableHolePunching(),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create host: %w", err)
	}

	// 3. Setup DHT for network routing and peer discovery
	kademliaDHT, err := dht.New(ctx, h)
	if err != nil {
		h.Close()
		return nil, fmt.Errorf("failed to create dht: %w", err)
	}

	if err = kademliaDHT.Bootstrap(ctx); err != nil {
		h.Close()
		return nil, fmt.Errorf("failed to bootstrap dht: %w", err)
	}

	// 4. Create PubSub with GossipSub
	ps, err := pubsub.NewGossipSub(ctx, h)
	if err != nil {
		h.Close()
		return nil, fmt.Errorf("failed to create pubsub: %w", err)
	}

	// Join the todo topic
	topic, err := ps.Join(TodoTopic)
	if err != nil {
		h.Close()
		return nil, fmt.Errorf("failed to join topic: %w", err)
	}

	// Subscribe to the topic
	sub, err := topic.Subscribe()
	if err != nil {
		h.Close()
		return nil, fmt.Errorf("failed to subscribe: %w", err)
	}

	node := &Node{
		ctx:    ctx,
		Host:   h,
		PubSub: ps,
		Topic:  topic,
		Sub:    sub,
		DHT:    kademliaDHT,
		PeerID: h.ID().String(),
		peers:  make(map[peer.ID]struct{}),
	}

	// Setup mDNS discovery
	if err := node.setupMDNS(); err != nil {
		h.Close()
		return nil, fmt.Errorf("failed to setup mdns: %w", err)
	}

	// Start listening for messages
	go node.readLoop()

	return node, nil
}

// loadOrGenerateKey manages the node's private key persistence
func loadOrGenerateKey(dataDir string) (crypto.PrivKey, error) {
	keyPath := filepath.Join(dataDir, "priv.key")

	// Try loading existing key
	data, err := os.ReadFile(keyPath)
	if err == nil {
		return crypto.UnmarshalPrivateKey(data)
	}

	// Generate new key if not found
	fmt.Println("🔑 Generating new identity key...")
	priv, _, err := crypto.GenerateKeyPairWithReader(crypto.Ed25519, -1, rand.Reader)
	if err != nil {
		return nil, err
	}

	// Save the key
	data, err = crypto.MarshalPrivateKey(priv)
	if err != nil {
		return nil, err
	}

	err = os.WriteFile(keyPath, data, 0600)
	return priv, err
}

// setupMDNS sets up mDNS peer discovery
func (n *Node) setupMDNS() error {
	s := mdns.NewMdnsService(n.Host, ServiceTag, n)
	return s.Start()
}

// Connect manually connects to a peer via multiaddress
func (n *Node) Connect(addrStr string) error {
	addr, err := multiaddr.NewMultiaddr(addrStr)
	if err != nil {
		return fmt.Errorf("invalid address: %w", err)
	}

	info, err := peer.AddrInfoFromP2pAddr(addr)
	if err != nil {
		return fmt.Errorf("invalid peer address: %w", err)
	}

	ctx, cancel := context.WithTimeout(n.ctx, 15*time.Second)
	defer cancel()

	if err := n.Host.Connect(ctx, *info); err != nil {
		return err
	}

	// If we connect manually, we should also track it
	n.mu.Lock()
	n.peers[info.ID] = struct{}{}
	n.mu.Unlock()

	// Trigger sync
	if n.OnPeerConnected != nil {
		go n.OnPeerConnected()
	}

	return nil
}

// HandlePeerFound implements mdns.Notifee
func (n *Node) HandlePeerFound(pi peer.AddrInfo) {
	if pi.ID == n.Host.ID() {
		return // Ignore self
	}

	// Filter out addresses that are likely ourselves (matching our own listening addresses)
	// This helps with the "Noise handshake" error when discovering old versions of ourselves on the same machine
	n.mu.Lock()
	_, exists := n.peers[pi.ID]
	n.mu.Unlock()

	if exists {
		return // Already connected
	}

	fmt.Printf("🔍 Discovered peer: %s\n", pi.ID.String()[:8])

	// Connect to peer
	ctx, cancel := context.WithTimeout(n.ctx, 10*time.Second)
	defer cancel()

	if err := n.Host.Connect(ctx, pi); err != nil {
		// Only log failure if it's not a self-connection error we're trying to avoid
		fmt.Printf("❌ Failed to connect to peer %s: %v\n", pi.ID.String()[:8], err)
		return
	}

	n.mu.Lock()
	n.peers[pi.ID] = struct{}{}
	n.mu.Unlock()

	fmt.Printf("✓ Connected to peer: %s\n", pi.ID.String()[:8])

	// Notify that a new peer connected - this triggers sync
	if n.OnPeerConnected != nil {
		// Small delay to ensure pubsub is ready
		go func() {
			time.Sleep(500 * time.Millisecond)
			n.OnPeerConnected()
		}()
	}
}

// readLoop reads messages from pubsub
func (n *Node) readLoop() {
	for {
		msg, err := n.Sub.Next(n.ctx)
		if err != nil {
			if n.ctx.Err() != nil {
				return // Context cancelled
			}
			continue
		}

		// Ignore our own messages
		if msg.ReceivedFrom == n.Host.ID() {
			continue
		}

		// Call message handler
		if n.OnMessage != nil {
			n.OnMessage(msg.Data)
		}
	}
}

// Broadcast sends a message to all peers
func (n *Node) Broadcast(msgType MessageType, payload []byte) error {
	msg := Message{
		Type:    msgType,
		From:    n.PeerID,
		Payload: payload,
	}

	data, err := json.Marshal(msg)
	if err != nil {
		return err
	}

	return n.Topic.Publish(n.ctx, data)
}

// RequestSync broadcasts a sync request to all peers
func (n *Node) RequestSync() error {
	return n.Broadcast(MsgSyncRequest, nil)
}

// PeerCount returns the number of connected peers
func (n *Node) PeerCount() int {
	n.mu.RLock()
	defer n.mu.RUnlock()
	return len(n.peers)
}

// Close shuts down the node
func (n *Node) Close() error {
	return n.Host.Close()
}

// Addresses returns the node's multiaddresses
func (n *Node) Addresses() []string {
	var addrs []string
	for _, addr := range n.Host.Addrs() {
		addrs = append(addrs, fmt.Sprintf("%s/p2p/%s", addr, n.Host.ID()))
	}
	return addrs
}
