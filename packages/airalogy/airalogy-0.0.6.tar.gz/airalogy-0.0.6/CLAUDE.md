# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the `airalogy` Python package - the world's first universal framework for standardized data digitization. It enables creating custom protocols for defining how data is collected, validated, and processed in research contexts.

Key components:
- **Airalogy Markdown (AIMD)**: Define data fields in Markdown with variables (`{{var}}`), steps (`{{step}}`), and checkpoints (`{{check}}`)
- **Model-based Validation**: Pydantic models for strict type checking with built-in types like `UserName`, `CurrentTime`, file IDs, etc.
- **Assigner System**: Declarative `@assigner` decorators for auto-computation of field values

## Development Commands

### Setup and Dependencies
```bash
# Install dependencies using PDM
pdm install

# Install in development mode
pdm install --dev
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_assigner.py

# Run tests with coverage
pytest --cov=src/
```

### Linting and Formatting
```bash
# Format code with ruff
ruff format .

# Lint with ruff
ruff check .

# Auto-fix lint issues
ruff check --fix .
```

### Building and Packaging
```bash
# Build package with hatchling
python -m build

# Install locally for testing
pip install -e .
```

## Code Architecture

### Core Modules

1. **`src/airalogy/airalogy/`** - Main client for interacting with the Airalogy platform
   - File upload/download functionality
   - Record retrieval from the platform

2. **`src/airalogy/aimd/`** - Airalogy Markdown parser
   - Parses `.aimd` files to extract variables, steps, and checkpoints
   - Validates field names and structure

3. **`src/airalogy/assigner/`** - Auto-computation system
   - `AssignerBase` class with `@assigner` decorator
   - `AssignerResult` for return values
   - Dependency resolution and execution modes

4. **`src/airalogy/built_in_types/`** - Special data types
   - File ID types for different file formats
   - User identity, timestamps, and metadata types
   - Special handling types like `IgnoreStr` and `Recommended`

5. **`src/airalogy/models/`** - Core data models
   - Record, step, and check models
   - Pydantic-based validation schemas

### Key Patterns

1. **Protocol Structure**
   ```
   protocol/
   ├─ protocol.aimd     # Airalogy Markdown definitions
   ├─ model.py          # Pydantic validation models
   └─ assigner.py       # Auto-computation logic
   ```

2. **Assigner Implementation**
   ```python
   class Assigner(AssignerBase):
       @assigner(
           assigned_fields=["output_field"],
           dependent_fields=["input_field1", "input_field2"],
           mode="auto"  # or "manual"
       )
       def compute_output(dependent_fields: dict) -> AssignerResult:
           # computation logic
           return AssignerResult(assigned_fields={"output_field": value})
   ```

3. **Built-in Types Usage**
   ```python
   from airalogy.built_in_types import UserName, CurrentTime, FileIdPNG
   
   class ProtocolModel(BaseModel):
       researcher: UserName
       timestamp: CurrentTime
       data_file: FileIdPNG
   ```

## Common Development Tasks

### Adding New Built-in Types
1. Create new type in `src/airalogy/built_in_types/`
2. Export in `__init__.py`
3. Add to `__all__` list

### Extending Assigner Functionality
1. Modify `AssignerBase` in `src/airalogy/assigner/assigner_base.py`
2. Update tests in `tests/test_assigner.py`

### Working with AIMD Files
1. Parser logic in `src/airalogy/aimd/parser.py`
2. Test cases in `tests/test_aimd/`

## Testing Approach

Tests are written using pytest and organized by module:
- Unit tests for assigner logic in `tests/test_assigner.py`
- AIMD parser tests in `tests/test_aimd/`
- Model validation tests in respective model test files

Run tests with `pytest` command from the project root.