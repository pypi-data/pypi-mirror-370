# Bear Utils - AI Coding Agent Instructions

## Project Overview

Bear Utils is a modular Python utility library organized into focused packages. The codebase follows a strict architectural pattern with centralized exports via `__init__.py` files and protocol-driven interfaces.

## Build System & Workflows

### Development Environment
- **UV package manager**: Primary dependency management (`uv sync`, `uv add`, `uv build`)
- **Mask task runner**: Custom commands in `maskfile.md` (run with `mask <command>`)
- **Nox sessions**: Cross-platform testing and linting (`nox -s <session>`)

### Critical Commands
```bash
# Development setup
uv sync

# Testing & Quality
mask test                    # Quick pytest run
nox -s tests                # Full multi-Python testing  
nox -s ruff_check           # CI linting (read-only)
nox -s ruff_fix             # Development linting (auto-fix)
nox -s coverage             # Test coverage with HTML report

# Release workflow
mask bump patch             # Version bump + git tag
mask build                  # UV build package
mask publish                # Publish to PyPI
```

## Architecture Patterns

### Module Organization
- **Centralized exports**: All public APIs exposed through package `__init__.py` files
- **Protocol-driven design**: Core interfaces in `logger_protocol.py`, `_lazy_typing.py`
- **Internal separation**: Private implementation in `_internal/` (CLI, versioning, debug)
- **Optional dependencies**: GUI features require `[gui]` extra (`pyqt6`)

### Key Components Structure
```
src/bear_utils/
├── _internal/          # CLI, versioning, debug utilities
├── cache/              # Diskcache wrapper with decorator pattern
├── config/             # TinyDB-based settings with dot notation access
├── database/           # SQLAlchemy wrapper with singleton pattern
├── logger_manager/     # Rich-based multi-logger system
├── events/             # Pub/sub event system (sync/async)
├── files/              # Factory pattern for file type handlers
├── time/               # Epoch timestamp and time utilities
└── gui/                # Optional PyQt6 dialogs
```

### Configuration Management Patterns

**ConfigManager**: TOML-based application configuration
- Pydantic model validation with type safety
- Environment variable overrides (e.g., `MYAPP_DATABASE_HOST`)
- Multi-file loading: `default.toml` → `{env}.toml` → `local.toml`
- Deep merge with environment precedence

**SettingsManager**: User settings and runtime state
- TinyDB backend with in-memory caching
- Dot notation access: `settings.some_key = value`
- Auto-sync with file hash validation
- Global singleton via `get_settings_manager()`

### Logger Manager System

**Architecture Overview:**
The logging system is built around protocol-driven design with `LoggerProtocol` and `AsyncLoggerProtocol` interfaces, enabling consistent behavior across different logger implementations.

**Custom Log Levels:**
Extended beyond standard Python logging with Rich-styled levels:
- `VERBOSE` (5): Detailed debugging information
- `DEBUG` (10): Standard debug information  
- `SUCCESS` (15): Success operations
- `INFO` (20): General information
- `WARNING` (30): Warning conditions
- `ERROR` (40): Error conditions
- `FAILURE` (45): Critical failures

**Logger Implementations:**

1. **ConsoleLogger**: Rich-enhanced console output with Python's logging framework
   - Queue-based async logging with `QueueListener`
   - Optional file rotation (`RotatingFileHandler`)
   - Interactive prompt integration via `PromptSession`
   - Rich traceback formatting with local variables
   - Singleton pattern with `get_instance(init=True)`

2. **BaseLogger**: Foundation class for all loggers
   - Style-aware output with configurable themes
   - Stack level tracking for accurate caller information
   - Buffer console for styled string capture
   - Dynamic method generation for log levels

3. **FileLogger**: File-based logging with rotation
   - Configurable file size limits (default: 5MB)
   - Automatic log rotation and backup
   - Custom formatters for structured output

4. **BufferLogger**: In-memory log storage
   - Deque-based message buffering
   - Retrievable log history
   - Memory-efficient with configurable limits

5. **LoggingServer/LoggingClient**: FastAPI-based distributed logging
   - HTTP endpoint for remote log aggregation
   - Pydantic models for request validation
   - Async client for non-blocking log transmission
   - Singleton server with configurable host/port

**Usage Patterns:**
```python
# Console logging with Rich styling
logger = ConsoleLogger.get_instance(init=True, level=DEBUG, verbose=True)
logger.success("Operation completed")  # Green styled output
logger.failure("Critical error")       # Red underlined output

# Distributed logging setup
server = LoggingServer(host="localhost", port=8080, log_file="app.log")
client = LoggingClient(base_url="http://localhost:8080")
await client.log(LogLevel.INFO, "Remote log message")

# Factory-based logger creation
from bear_utils.logger_manager.loggers import LoggerFactory
logger = LoggerFactory.create_logger("file", file_path="app.log", level=INFO)
```

**Theme Customization:**
Rich themes control styling with method-specific styles defined in `LOGGER_METHODS`:
```python
# Custom theme with overrides
custom_theme = Theme({
    "info": "bold cyan",
    "error": "bold red on yellow", 
    "success": "bold green underline"
})
logger = ConsoleLogger(theme=custom_theme)
```

## Development Conventions

### Code Style (Ruff Configuration)
- **Line length**: 120 characters
- **Target**: Python 3.13+
- **Import organization**: `future` → `standard-library` → `third-party` → `first-party` → `local-folder`
- **Type hints**: Comprehensive typing required (ANN rules enabled)

### Testing Patterns
- **Pytest**: Standard test framework with `pytest-asyncio` for async tests
- **Test location**: `tests/test_<module>.py` structure
- **Visual tests**: Use `@pytest.mark.visual` for manual verification tests
- **Coverage**: HTML reports generated in `htmlcov/`

### File Handling Factory
```python
# Automatic handler selection based on file extension
factory = FileHandlerFactory()
handler = factory.get_handler(Path("config.json"))  # Gets JSONHandler
data = handler.read_file()
```

### Cache Decorator Usage
```python
# Factory pattern with configuration
@cache_factory(directory="~/.cache/my_app", default_timeout=3600)
def expensive_function(arg1, arg2):
    return computed_result

# Or instance-based
cache = CacheWrapper(directory="~/.cache/my_app")
cache.set("key", value, expire=60)
```

## Key Integration Points

### Version Management
- **Dynamic versioning**: UV-dynamic-versioning from git tags
- **CLI access**: `python -m bear_utils get-version` or `bear-utils get-version`
- **Bump workflow**: `mask bump [patch|minor|major]` creates git tags

### Configuration & Settings Systems
- **Application config**: `ConfigManager(config_model, "app_name")` for TOML-based setup
- **User settings**: `get_settings_manager()` singleton for runtime preferences
- **Config locations**: `~/.config/{app_name}/` with environment overrides
- **Settings location**: `~/.config/bear_utils/` by default

### Event System Integration
```python
# Registration patterns
@subscribe("event_name")
def sync_handler(data): pass

@subscribe("event_name") 
async def async_handler(data): pass

# Publishing
publish("event_name", data)  # Handles both sync/async automatically
```

## Common Debugging Workflows

### Development Debugging
- `python -m bear_utils --debug_info` - Full environment info
- `nox -s coverage` - Generate coverage reports for test gaps
- Test individual modules: `pytest tests/test_<specific>.py -v`

### Build Issues
- Clean build artifacts: `mask clean`
- Dependency conflicts: `uv lock --upgrade`
- Type checking: `nox -s pyright`

## Dependencies & Constraints
- **Core dependencies**: SQLAlchemy 2.x, Rich 14.x, Pydantic 2.x, diskcache
- **Optional GUI**: PyQt6 (separate installation group)
- **Python version**: 3.12+ required, tested on 3.13/3.14
- **Build backend**: Hatchling with UV dynamic versioning
