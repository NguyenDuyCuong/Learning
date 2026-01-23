package crdt

import (
	"encoding/json"
	"os"
	"sync"
)

// Todo represents a single todo item
type Todo struct {
	ID        string `json:"id"`
	Title     string `json:"title"`
	Done      bool   `json:"done"`
	Timestamp int64  `json:"timestamp"` // Unix nano for LWW
	Author    string `json:"author"`    // Peer ID who created/modified
}

// Store is a LWW-Map based CRDT store for todos
type Store struct {
	mu       sync.RWMutex
	todos    map[string]*Todo // ID -> Todo
	filePath string
	onChange func() // callback when state changes
}

// NewStore creates a new CRDT store
func NewStore(filePath string) *Store {
	s := &Store{
		todos:    make(map[string]*Todo),
		filePath: filePath,
	}
	s.load()
	return s
}

// SetOnChange sets a callback for when the store changes
func (s *Store) SetOnChange(fn func()) {
	s.onChange = fn
}

// Add adds or updates a todo using LWW semantics
func (s *Store) Add(todo *Todo) bool {
	s.mu.Lock()
	defer s.mu.Unlock()

	existing, exists := s.todos[todo.ID]
	if exists && existing.Timestamp >= todo.Timestamp {
		// Existing version is newer or equal, ignore
		return false
	}

	s.todos[todo.ID] = todo
	s.persist()

	if s.onChange != nil {
		s.onChange()
	}

	return true
}

// Get returns a todo by ID
func (s *Store) Get(id string) *Todo {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return s.todos[id]
}

// List returns all todos
func (s *Store) List() []*Todo {
	s.mu.RLock()
	defer s.mu.RUnlock()

	result := make([]*Todo, 0, len(s.todos))
	for _, t := range s.todos {
		result = append(result, t)
	}
	return result
}

// MarkDone marks a todo as done
func (s *Store) MarkDone(id string, author string, timestamp int64) bool {
	s.mu.Lock()
	defer s.mu.Unlock()

	existing, exists := s.todos[id]
	if !exists {
		return false
	}

	if existing.Timestamp >= timestamp {
		return false // Already have newer version
	}

	existing.Done = true
	existing.Timestamp = timestamp
	existing.Author = author
	s.persist()

	if s.onChange != nil {
		s.onChange()
	}

	return true
}

// Delete removes a todo (by marking with special timestamp)
func (s *Store) Delete(id string) {
	s.mu.Lock()
	defer s.mu.Unlock()
	delete(s.todos, id)
	s.persist()
}

// Merge merges another store's state into this one (CRDT merge)
func (s *Store) Merge(todos []*Todo) int {
	merged := 0
	for _, t := range todos {
		if s.Add(t) {
			merged++
		}
	}
	return merged
}

// GetState returns all todos for syncing
func (s *Store) GetState() []*Todo {
	return s.List()
}

// persist saves state to file
func (s *Store) persist() {
	data, err := json.MarshalIndent(s.todos, "", "  ")
	if err != nil {
		return
	}
	os.WriteFile(s.filePath, data, 0644)
}

// load loads state from file
func (s *Store) load() {
	data, err := os.ReadFile(s.filePath)
	if err != nil {
		return
	}
	json.Unmarshal(data, &s.todos)
}
