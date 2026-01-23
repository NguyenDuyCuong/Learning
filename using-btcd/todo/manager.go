package todo

import (
	"crypto/rand"
	"encoding/hex"
	"time"

	"p2p-todo/crdt"
)

// Manager handles todo operations
type Manager struct {
	store  *crdt.Store
	peerID string
}

// NewManager creates a new todo manager
func NewManager(store *crdt.Store, peerID string) *Manager {
	return &Manager{
		store:  store,
		peerID: peerID,
	}
}

// Add creates a new todo
func (m *Manager) Add(title string) *crdt.Todo {
	todo := &crdt.Todo{
		ID:        generateID(),
		Title:     title,
		Done:      false,
		Timestamp: time.Now().UnixNano(),
		Author:    m.peerID,
	}
	m.store.Add(todo)
	return todo
}

// MarkDone marks a todo as done
func (m *Manager) MarkDone(id string) bool {
	return m.store.MarkDone(id, m.peerID, time.Now().UnixNano())
}

// List returns all todos
func (m *Manager) List() []*crdt.Todo {
	return m.store.List()
}

// Delete removes a todo
func (m *Manager) Delete(id string) {
	m.store.Delete(id)
}

// generateID creates a short random ID
func generateID() string {
	b := make([]byte, 4)
	rand.Read(b)
	return hex.EncodeToString(b)
}
