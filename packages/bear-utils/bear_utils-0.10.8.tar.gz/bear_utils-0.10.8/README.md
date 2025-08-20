# Bear Utils

Personal set of tools and utilities for Python projects, focusing on modularity and ease of use. This library includes components for caching, database management, logging, time handling, file operations, CLI prompts, image processing, clipboard interaction, gradient utilities, event systems, and async helpers.

## Overview

Bear Utils is a collection of utility modules I've created for common tasks across my Python projects. The library is designed to be modular and easy to use, with each component focusing on a specific functionality.

## Installation

```bash
pip install bear-util.      # Core package (recommended for most users)
pip install bear-utils[gui] # With optional GUI functionality

# Using UV
uv add bear-utils                    # Core only
uv add bear-utils --group gui        # With GUI functionality
```

## Key Components

### Cache Management

The `cache` package provides disk cache functionality via `diskcache`:

```python
from bear_utils.cache import CacheWrapper, cache_factory

# Create a cache instance
cache = Cache(directory="~/.cache/my_app")

# Use the cache factory to create a decorated function
@cache_factory(directory="~/.cache/my_app")
def expensive_function(arg1, arg2):
    # Function will be cached based on arguments
    pass
```

### Database Management

The `database` package provides SQLAlchemy integration with helpful patterns:

```python
from bear_utils.database import DatabaseManager
from sqlalchemy import Column, Integer, String

# Get declarative base
Base = DatabaseManager.get_base()

# Define models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)

# Create and use database
db = DatabaseManager("sqlite:///app.db")
with db.session() as session:
    session.add(User(name="test"))
    session.commit()
```

### Logging

The `logging` package provides an enhanced console logger using rich:

```python
from bear_utils.logger_manager import ConsoleLogger

logger = ConsoleLogger()
logger.info("Information message")
logger.error("Error message") 
logger.warning("Warning message")
```

### Time Management

The `time` package contains tools for time handling and measurement:

```python
from bear_utils.time import TimeTools, EpochTimestamp

# Get current timestamp
now = EpochTimestamp()

# Time function execution
from bear_utils.time.time_manager import timer

with timer(name="my_operation"):
    # Code to measure
    pass
```

### File Handling

The `files` package provides abstractions for working with different file types:

```python
from pathlib import Path
from bear_utils.files.file_handlers import FileHandlerFactory

factory = FileHandlerFactory()
handler = factory.get_handler(Path("config.json"))
data = handler.read_file()
```

### Prompt Helpers

Utilities for creating interactive command-line prompts:

```python
from bear_utils.cli.prompt_helpers import restricted_prompt

choice = restricted_prompt(
    message="Select an option:", 
    valid_options=["option1", "option2"]
)
```

### GUI Utilities (Optional)

**Note: GUI functionality requires the optional PyQt6 dependency. Install with `pip install bear-utils[gui]`**

The `gui` package provides PyQt6-based dialog utilities for desktop applications:

```python
# Color picker dialog
from bear_utils.gui import select_color

color_info = select_color(
    initial_color="#FF5733", 
    title="Choose a Color"
)
if color_info:
    print(f"Selected: {color_info.hex}")  # e.g., "#FF5733"
    print(f"RGB: {color_info.rgb}")       # ColorTriplet(255, 87, 51)
    print(f"RGBA: {color_info.rgba}")     # (255, 87, 51, 255)

# Text input dialog
from bear_utils.gui import get_text

user_input = get_text(
    title="Input Required",
    label="Enter your name:",
    default="Default text"
)

# Qt Application wrapper
from bear_utils.gui import QTApplication

app = QTApplication(
    app_name="My App",
    org_name="My Organization"
)
```

**Error handling**: If PyQt6 is not installed, importing GUI components will raise a helpful error:
```
ImportError: PyQt6 is required for GUI functionality. Install it with: pip install bear-utils[gui]
```

### Image Helpers

Utilities for working with images are located in the `graphics` package:

```python
from pathlib import Path
from bear_utils.graphics import encode_image_to_jpeg, encode_image_to_png

# Encode image to base64 string
jpeg_data = encode_image_to_jpeg(Path("image.jpg"), max_size=800)
png_data = encode_image_to_png(Path("image.png"), max_size=800)
```

### Clipboard Helpers

`bear_utils.extras._tools` includes simple helpers for interacting with the system clipboard:

```python
from bear_utils.extras._tools import copy_to_clipboard, paste_from_clipboard

copy_to_clipboard("hello world")
text = paste_from_clipboard()
```

Supported platforms include macOS (`pbcopy/pbpaste`), Windows (`clip`/`powershell Get-Clipboard`),
and Linux with either Wayland (`wl-copy`/`wl-paste`) or X11 (`xclip`).

### Gradient Utilities

The `graphics.bear_gradient` module provides color gradient functionality for the purposes of visualizing data or creating color transitions:

```python
from bear_utils.graphics import ColorGradient, RichColor
from rich.console import Console
from rich.color_triplet import ColorTriplet

console = Console()

# Health meter goes from red (low health) to green (full health)
health_gradient = ColorGradient()

console.print("🏥 [bold]Health Meter Demonstration[/bold] 🏥\n")

# Normal health: Red (low) -> Green (high)
console.print("[bold green]Normal Health Levels (0% = Critical, 100% = Perfect):[/bold green]")
for health in range(0, 101, 10):
    color: ColorTriplet = health_gradient.map_to_color(0, 100, health)
    health_bar = "█" * (health // 5)
    console.print(f"HP: {health:3d}/100 {health_bar:<20}", style=color.rgb)

console.print("\n" + "="*50 + "\n")

# Reversed: Infection/Damage meter (Green = good, Red = bad)
console.print("[bold red]Infection Level (0% = Healthy, 100% = Critical):[/bold red]")
health_gradient.reverse = True
for infection in range(0, 101, 10):
    color: ColorTriplet = health_gradient.map_to_color(0, 100, infection)
    infection_bar = "█" * (infection // 5)
    status = "🦠" if infection > 70 else "⚠️" if infection > 30 else "✅"
    console.print(f"Infection: {infection:3d}% {infection_bar:<20} {status}", style=color.rgb)

health_scenarios = [
    (5, "💀 Nearly Dead"),
    (25, "🩸 Critical Condition"), 
    (50, "⚠️  Wounded"),
    (75, "😐 Recovering"),
    (95, "💪 Almost Full Health"),
    (100, "✨ Perfect Health")
]

console.print("[bold green]Health Status Examples:[/bold green]")
for hp, status in health_scenarios:
    color: ColorTriplet = health_gradient.map_to_color(0, 100, hp)
    console.print(f"{status}: {hp}/100 HP", style=color.rgb)
```

### Event System

The `events` module provides a pub/sub event system that supports both synchronous and asynchronous handlers:

```python
from bear_utils.events.events_module import subscribe, publish

# Subscribe to events
@subscribe("user_logged_in")
def handle_login(user_id):
    print(f"User {user_id} logged in")

# Publish events
publish("user_logged_in", 12345)

# Async support
@subscribe("data_processed")
async def handle_process(data):
    await process_async(data)

# Clear handlers
from bear_utils.events.events_module import clear_handlers_for_event
clear_handlers_for_event("user_logged_in")
```

### Async Helpers

The `extras/_async_helpers.py` module provides utility functions for working with async code:

```python
from bear_utils.extras._async_helpers import is_async_function

def handle_function(func):
    if is_async_function(func):
        # Handle async function
        pass
    else:
        # Handle sync function
        pass
```
