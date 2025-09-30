# sgit

**sgit** is a minimal Git implementation in Python that replicates core functionalities of Git, providing a lightweight version control system for learning and experimentation. It allows users to initialize repositories, track files, make commits, add branches, and view repository status using a command-line interface.

---

## Features

* **Repository Initialization**: `sgit init` to create a new repository.
* **Staging Area**: `sgit add` and `sgit rm` for managing tracked files.
* **Commits**: Create commits with `sgit commit`, including author metadata and timestamps.
* **Branching & References**: Supports HEAD, branches, and tags.
* **Checkout**: `sgit checkout` to restore files and switch branches.
* **Logs**: `sgit log` with Graphviz-compatible output for visualizing commit history.
* **Status**: `sgit status` to view changes staged, unstaged, and untracked.
* **Ignore Rules**: `.gitignore` parsing and global/local ignore support.
* **Object Storage**: Implements Git object types (`blob`, `tree`, `commit`, `tag`) with SHA-1 hashing and zlib compression.
* **Cross-Platform Support**: Works on Linux, and it's other distros.

---

## Project Structure

```
sgit/
├── sgit/
│   ├── cli/             # Command-line interface
│   ├── core/            # Git objects, index, refs, repository
│   ├── operations/      # Command implementations
│   └── utils/           # Helpers: hashing, file IO, gitignore, config
└── README.md
```

**Layered Architecture**:

* **CLI Layer**: Parses arguments and dispatches commands.
* **Operations Layer**: Implements Git-like commands.
* **Core Layer**: Handles Git objects and internal repository structures.
* **Utils Layer**: Provides helpers for serialization, hashing, and filesystem interactions.

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Shishank93774/sgit
cd sgit
bash install.sh
```
*Commands to further proceed will be shown there.*

---

## Object Model

* **Blob**: Stores file contents.
* **Tree**: Represents directories and file hierarchy.
* **Commit**: Stores snapshot of repository at a point in time.
* **Tag**: Named references to commits.

All objects are stored in `.sgit/objects` using SHA-1 hash as the identifier and compressed with zlib.

---

## Highlights & Learning Outcomes

* Built **core Git functionality from scratch** in Python.
* Implemented **efficient storage** with SHA-1 object hashing and compressed object files.
* Designed **modular architecture** with clear separation of CLI, operations, core objects, and utilities.
* Gained deep understanding of **version control internals**, including commits, trees, and the staging area.

---

## Future Improvements

* Branching and merging with conflict resolution.
* Remote repository support (push/pull).
* Interactive rebase and cherry-pick.
* Enhanced CLI with color-coded output and progress bars.

---

## Author

**Shishank Rawat** – Business Analyst with a crunch to core Software development.
