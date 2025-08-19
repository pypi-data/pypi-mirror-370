# MEMG 🧠⚡

**True memory for AI - lightweight, generalist, AI-made, AI-focused**

MEMG is a lightweight memory management system that provides persistent memory capabilities for AI agents and applications. Built on top of the robust [memg-core](https://pypi.org/project/memg-core/) foundation, MEMG adds enhanced APIs, integration tools, and seamless development experience for structured memory operations.

## 🚀 Quick Start

```bash
pip install memg
```

```python
import memg

# Add memories with structured data
memory = memg.add_memory("task", {
    "statement": "Implement user authentication system",
    "details": "Need to add JWT-based auth with role management",
    "priority": "high"
}, user_id="your_user_id")

# Search memories with keywords
results = memg.search("authentication", user_id="your_user_id")

# Create memory configuration from YAML
memory_config = memg.create_memory_from_yaml("config/my_config.yaml")
```

## ✨ Key Features

### 🎯 **Structured Memory Management**
- **Vector Search**: Semantic search capabilities with relevance scoring
- **Graph Storage**: Efficient relationship tracking between memories
- **Schema Validation**: YAML-based memory schemas with type safety

### 🏗️ **Built on Solid Foundation**
- **memg-core Integration**: Leverages battle-tested core memory management
- **Production Ready**: Comprehensive testing, quality tools, and CI/CD
- **Modern Architecture**: Clean separation between core storage and enhanced features

### 🔌 **Flexible Integration**
- **Python SDK**: Clean Python API built on memg-core
- **YAML Configuration**: Flexible schema definition and management
- **Cross-platform**: Works on all major operating systems

### 🛠️ **Developer Experience**
- **Rich Configuration**: YAML-based schemas and flexible setup
- **Comprehensive Testing**: Unit and integration test suites
- **Quality Tools**: Ruff, MyPy, Bandit for code quality
- **Type Safety**: Full type hints and runtime validation

## 📦 Architecture

```
MEMG Ecosystem
├── memg-core (PyPI)          # Foundation: storage, search, schemas
└── MEMG (this package)       # Enhanced APIs and utilities
```

### **Core Components**

- **`memg.core`**: Integration layer with memg-core
- **`memg.search`**: Search orchestration and utilities
- **`memg.api`**: High-level API interfaces
- **`memg.utils`**: Utilities and schema management

## 🎮 Usage Examples

### Basic Memory Operations

```python
import memg

# Create and store memories
memory = memg.add_memory("note", {
    "statement": "API design patterns research",
    "details": "Investigated REST vs GraphQL for user management API",
    "project": "web-app"
}, user_id="your_user_id")

# Search memories by keyword
results = memg.search("API design", user_id="your_user_id")

# Delete memories when no longer needed
memg.delete_memory(memory.memory_id, user_id="your_user_id")
```

### Configuration and Schema Management

```python
import memg

# Get current memory configuration
config = memg.get_config()

# Load configuration from YAML file
memory_system = memg.create_memory_from_yaml("config/custom_schema.yaml")

# Work with memory objects
for result in memg.search("project tasks", user_id="your_user_id"):
    print(f"Memory: {result.payload['statement']}")
    print(f"Score: {result.score}")
```

### Working with Search Results

```python
import memg

# Search returns structured results
results = memg.search("authentication tasks", user_id="your_user_id")

for result in results:
    print(f"Type: {result.memory_type}")
    print(f"Content: {result.payload['statement']}")
    print(f"Relevance Score: {result.score}")
    print(f"Memory ID: {result.memory_id}")
```

## 🏁 Getting Started

### Installation

```bash
# Install MEMG
pip install memg

# For development setup
git clone https://github.com/genovo-ai/memg.git
cd memg
pip install -e ".[dev]"
```

### Configuration

Create a memory configuration:

```yaml
# config/my_config.yaml
entities:
  task:
    required: [statement]
    optional: [assignee, priority, status, due_date]
  note:
    required: [statement, details]
    optional: [project, tags]
```

```python
import memg

# Initialize with custom configuration
memory = memg.create_memory_from_yaml("config/my_config.yaml")
```

### Memory Server

For development and testing:

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests to verify installation
python -m pytest tests/
```

## 🔧 Development

### Quality Tools

```bash
# Run all quality checks
make quality-check

# Individual tools
make lint          # Ruff linting
make typecheck     # MyPy type checking
make security      # Bandit security scan
make test          # Full test suite
```

### Testing

```bash
# Run tests
make test-all

# Fast tests only
make test-fast

# Integration tests
make test-integration

# Coverage report
make test-coverage
```

## 🤝 Contributing

We welcome contributions! Please see our development workflow:

1. **Fork & Clone**: Fork the repository and clone locally
2. **Setup**: `pip install -e ".[dev]"` for development dependencies
3. **Quality**: Run `make quality-check` before committing
4. **Test**: Ensure `make test-all` passes
5. **PR**: Submit a pull request with clear description

### Development Standards

- **Code Quality**: Ruff formatting and linting
- **Type Safety**: MyPy type checking required
- **Security**: Bandit security scanning
- **Testing**: Comprehensive test coverage
- **Documentation**: Clear docstrings and examples

## 📚 Documentation

- **API Reference**: Coming soon
- **Architecture Guide**: See `src/memg/` for component structure
- **Integration Guide**: Coming soon
- **Configuration**: Explore `config/` directory for examples

## 🛡️ Security

- **Bandit Scanning**: Automated security vulnerability detection
- **Dependency Management**: Regular security updates
- **Input Validation**: Comprehensive data validation
- **Safe Defaults**: Secure-by-default configuration

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🌟 Related Projects

- **[memg-core](https://pypi.org/project/memg-core/)**: Foundation memory management system

---

**Built with ❤️ by the MEMG Team**

*True memory for AI - making intelligent agents truly intelligent* 🧠✨
