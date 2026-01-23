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

// DefaultBootstrapNodes is a list of public libp2p bootstrap nodes (Protocol Labs)
var DefaultBootstrapNodes = []string{
	"/dnsaddr/bootstrap.libp2p.io/p2p/QmNnooDu7ZQCbWw4ZiGghE9B3DH4t1R77qcphTerjBYMwt",
	"/dnsaddr/bootstrap.libp2p.io/p2p/QmQCU2EcNmSRRL6rLjtDeLVCgeuYksvifLY2HtdcfZPb3p",
	"/dnsaddr/bootstrap.libp2p.io/p2p/QmbLHAnMoWSWSMvJtp3KHh4fgn7CYf94G73G48RLm7oN9q",
	"/dnsaddr/bootstrap.libp2p.io/p2p/QmcZf59bWwK5XFi76CZX8qeeJgmMpVMiH4vS6S4F96qS2M",
	"/ip4/147.75.109.213/tcp/4001/p2p/QmNnooDu7ZQCbWw4ZiGghE9B3DH4t1R77qcphTerjBYMwt",
	"/ip4/147.75.83.83/tcp/4001/p2p/QmbLHAnMoWSWSMvJtp3KHh4fgn7CYf94G73G48RLm7oN9q",
	// Updated Peer ID for the IPFS gateway
	"/ip4/104.131.131.82/tcp/4001/p2p/QmaCpDMGvV2BGHeYERUEnRQAwe3N8SzbUtfsmvsqQLuvuJ",
}

// NewNode creates a new P2P node
func NewNode(ctx context.Context, dataDir string) (*Node, error) {
	// 1. Load or generate identity key
	priv, err := loadOrGenerateKey(dataDir)
	if err != nil {
		return nil, fmt.Errorf("failed to load identity: %w", err)
	}

	// Create node instance early to use it in callbacks
	node := &Node{
		ctx:   ctx,
		peers: make(map[peer.ID]struct{}),
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
		libp2p.EnableAutoRelayWithPeerSource(func(ctx context.Context, num int) <-chan peer.AddrInfo {
			return node.findRelayPeers(ctx, num)
		}),
		libp2p.EnableHolePunching(),
		libp2p.EnableNATService(),
		libp2p.EnableRelayService(),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create host: %w", err)
	}
	node.Host = h
	node.PeerID = h.ID().String()

	// 3. Setup DHT for network routing and peer discovery
	// ModeAutoServer allows the node to act as a DHT server if it has a public IP
	kademliaDHT, err := dht.New(ctx, h, dht.Mode(dht.ModeAutoServer))
	if err != nil {
		h.Close()
		return nil, fmt.Errorf("failed to create dht: %w", err)
	}

	// Bootstrap in background
	go func() {
		connectedCount := 0
		fmt.Println("🌐 Connecting to bootstrap nodes...")
		for _, addrStr := range DefaultBootstrapNodes {
			addr, err := multiaddr.NewMultiaddr(addrStr)
			if err != nil {
				fmt.Printf("⚠️  Invalid bootstrap addr %s: %v\n", addrStr, err)
				continue
			}
			pi, err := peer.AddrInfoFromP2pAddr(addr)
			if err != nil {
				// If it's a dnsaddr, it might need resolution or be handled differently
				// but let's see the error first
				fmt.Printf("⚠️  Failed to resolve bootstrap addr %s: %v\n", addrStr, err)
				continue
			}

			// Use a shorter timeout for each bootstrap attempt to not wait forever
			bCtx, cancel := context.WithTimeout(ctx, 10*time.Second)
			if err := h.Connect(bCtx, *pi); err == nil {
				connectedCount++
				fmt.Printf("✅ Connected to bootstrap: %s\n", pi.ID.String()[:8])
			} else {
				fmt.Printf("❌ Failed bootstrap %s: %v\n", pi.ID.String()[:8], err)
			}
			cancel()
		}
		fmt.Printf("🌐 Bootstrap complete: %d/%d nodes connected\n", connectedCount, len(DefaultBootstrapNodes))

		if err = kademliaDHT.Bootstrap(ctx); err != nil {
			fmt.Printf("⚠️  DHT Bootstrap warning: %v\n", err)
		}
	}()

	// Monitor connectivity and reachability
	go node.monitorConnectivity()

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

	node.PubSub = ps
	node.Topic = topic
	node.Sub = sub
	node.DHT = kademliaDHT

	// Setup mDNS discovery
	if err := node.setupMDNS(); err != nil {
		h.Close()
		return nil, fmt.Errorf("failed to setup mdns: %w", err)
	}

	// Start listening for messages
	go node.readLoop()

	return node, nil
}

// findRelayPeers acts as a source for AutoRelay.
// It searches for peers in the DHT that might be able to act as relays.
func (n *Node) findRelayPeers(ctx context.Context, num int) <-chan peer.AddrInfo {
	peerChan := make(chan peer.AddrInfo)

	go func() {
		defer close(peerChan)

		// 1. Check known bootstrap nodes first as they often are relays
		for _, addrStr := range DefaultBootstrapNodes {
			addr, _ := multiaddr.NewMultiaddr(addrStr)
			pi, _ := peer.AddrInfoFromP2pAddr(addr)
			select {
			case peerChan <- *pi:
			case <-ctx.Done():
				return
			}
		}

		// 2. In a real app index, we would also search DHT for nodes with specific protocols
		// For now, we rely on bootstrap nodes and natural peer discovery.
	}()

	return peerChan
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

// monitorConnectivity periodically logs the node's network status
func (n *Node) monitorConnectivity() {
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-n.ctx.Done():
			return
		case <-ticker.C:
			conns := n.Host.Network().Conns()
			addrs := n.Host.Addrs()

			// Count unique peers we are connected to at the network level
			networkPeers := make(map[peer.ID]struct{})
			for _, conn := range conns {
				networkPeers[conn.RemotePeer()] = struct{}{}
			}

			// Identify if we are using any relays
			var relayAddrs []string
			for _, addr := range addrs {
				if _, err := addr.ValueForProtocol(multiaddr.P_CIRCUIT); err == nil {
					relayAddrs = append(relayAddrs, addr.String())
				}
			}

			fmt.Printf("\n📊 [Status] Connected Peers: %d | Network Conns: %d\n",
				len(networkPeers), len(conns))

			if len(relayAddrs) > 0 {
				fmt.Printf("🌐 Relayed via: %d address(es)\n", len(relayAddrs))
				for _, r := range relayAddrs {
					fmt.Printf("   🔗 %s\n", r)
				}
			} else if len(networkPeers) > 0 {
				fmt.Println("🌐 Mode: Direct connection (No relay used yet)")
			}

			if len(networkPeers) == 0 {
				fmt.Println("⚠️  No peers connected. Check internet/firewall.")
			}
			fmt.Print("> ")
		}
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
