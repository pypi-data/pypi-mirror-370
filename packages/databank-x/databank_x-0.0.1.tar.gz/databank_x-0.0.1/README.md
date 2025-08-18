# Databank_X

A minimalistic, extensible database and encryption toolkit for Python

## Installation

```bash
pip install databank-x
```

## Quick Start

```python
from databank_x import basic, saves, security

# Initialize with sample data
basic.basic_List()

# Show current data
print(basic.show_List())

# Add new directory
basic.add_directory("my_data")

# Add data to directory
basic.add_data("Hello World", "my_data")

# Save to JSON
saves.save_json("my_database.json")
```

## Features

- Simple dictionary-based data management
- JSON file operations
- File encryption with Fernet
- Easy to use API

## Author

Micro (Micro444)
