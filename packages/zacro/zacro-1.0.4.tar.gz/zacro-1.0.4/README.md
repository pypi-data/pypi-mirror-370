# Zacro

[![CI](https://github.com/iory/zacro/actions/workflows/test.yml/badge.svg)](https://github.com/iory/zacro/actions/workflows/test.yml)
[![PyPI version](https://badge.fury.io/py/zacro.svg)](https://badge.fury.io/py/zacro)
[![Python versions](https://img.shields.io/pypi/pyversions/zacro.svg)](https://pypi.org/project/zacro/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Fast Rust implementation of xacro (XML macro language) with enhanced features for modular robotics.

## Overview

Zacro is a high-performance Rust implementation of the xacro XML macro language with enhanced features specifically designed for modular robotics applications. It provides:

- **Complete macro expansion**: Full support for xacro macro definitions and calls
- **Formatted output**: Optional XML formatting with proper indentation
- **Modular robot support**: Remove redundant first joints for modular robot assemblies
- **High performance**: Rust implementation for fast processing of large xacro files
- **Python bindings**: Easy-to-use Python API with both functional and class-based interfaces

## Features

- ✅ Complete macro expansion
- ✅ Property definitions and substitution
- ✅ Mathematical expressions
- ✅ File inclusion with package resolution
- ✅ Formatted XML output
- ✅ Modular robot first joint removal
- ✅ Python bindings
- ✅ Class-based and functional APIs

## Installation

```bash
pip install zacro
```

### From Source

```bash
git clone https://github.com/iory/zacro
cd zacro
pip install maturin
maturin develop --features python
```

## Quick Start

### Basic Usage

```python
import zacro

# Process xacro file to URDF
result = zacro.xacro_to_string("robot.xacro")

# Process with formatting
result = zacro.xacro_to_string("robot.xacro", format_output=True)

# Process from string
xml_string = """<?xml version="1.0"?>
<robot xmlns:xacro="http://ros.org/wiki/xacro">
  <xacro:macro name="box" params="name">
    <link name="${name}">
      <visual><geometry><box size="1 1 1"/></geometry></visual>
    </link>
  </xacro:macro>
  <xacro:box name="my_box"/>
</robot>"""

result = zacro.xacro_from_string(xml_string, format_output=True)
```

### Modular Robot Support

For modular robot xacro files where each module has a connection joint to its parent:

```python
# Remove redundant first joints in modular robot assemblies
result = zacro.xacro_to_string(
    "modular_robot.xacro",
    format_output=True,
    remove_first_joint=True
)
```

### Class-based API

```python
processor = zacro.XacroProcessor()
processor.set_format_output(True)
processor.set_remove_first_joint(True)

result = processor.process_file("robot.xacro")
```

## Building

### Prerequisites

- Rust 1.70+
- Python 3.8+ (for Python bindings)
- maturin (for Python bindings)

### Build Rust Library

```bash
cargo build --release
```

### Build Python Extension

```bash
maturin develop --features python
```

### Run Tests

```bash
cargo test
```
