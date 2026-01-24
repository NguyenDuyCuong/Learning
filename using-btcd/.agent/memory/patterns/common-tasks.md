# Common Tasks

This file documents repetitive tasks and their workflows for the P2P Todo project.

---

## Add a New CLI Command
**Files to modify:**
- `main.go`: Add the command to the switch statement in the CLI loop.
- `main.go`: Add the command to the `help` output.

**Steps:**
1. Identify the logic needed for the command.
2. Update the `switch cmd` block in `main.go`.
3. If necessary, add a corresponding method in `todo/manager.go` or `p2p/node.go`.
4. Update the help text.

---

## Update CRDT Data Model
**Files to modify:**
- `crdt/store.go`: Update the `Todo` struct.
- `todo/manager.go`: Update any logic that interacts with the `Todo` struct.
- `main.go`: Update CLI display logic if new fields are added.

**Steps:**
1. Add the new field to the `Todo` struct in `crdt/store.go`.
2. Ensure JSON tags are correctly set for serialization.
3. Update the `Merge` and `Add` logic if the new field affects conflict resolution.
4. Update display logic in `main.go`.

---

_No other tasks documented yet. Use "add task" command after completing repetitive tasks._
