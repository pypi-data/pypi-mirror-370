# MCard: Local-First Content Addressable Storage

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

MCard is a powerful Python library implementing an algebraically closed data structure for content-addressable storage. It provides a robust system where every piece of content is uniquely identified by its cryptographic hash and temporally ordered, enabling content verification, deduplication, and versioning.

The system features a modular architecture with support for multiple content types and a flexible database backend (SQLite).

## 📦 Data Model

MCard is built around a simple but powerful data model:

- **Card**: The fundamental unit of content with a unique hash
- **Hash**: Cryptographic identifier for content (SHA-256 by default)
- **Content**: Optimized BLOB storage
  - Binary format ensures maximum performance and exact content preservation
  - Efficient storage for both text and binary data
  - MCard's browsing interface provides human-readable views when needed
- **G-Time**: Global time value for temporal ordering of content claims
- **Temporal Ordering**: Built-in support for temporal ordering of content claims
- **Modular Architecture**: Extensible design with pluggable components
- **Type Safety**: Built with Python type hints and Pydantic models
- **Async Support**: Asynchronous API for improved performance

## ✨ Features

- **Content-Addressable Storage**: Store and retrieve content using cryptographic hashes (SHA-256 by default)
- **Optimized Storage**: BLOB format ensures maximum performance while MCard handles all text conversions
- **Content Type Detection**: Automatic detection of various file formats (JSON, XML, CSV, Markdown, Python, etc.)
- **Robust Binary Signatures**: Accurate detection of PNG, JPEG, GIF, PDF, ZIP/OpenXML, and RIFF (WAV/AVI) using raw-byte signatures (no lossy text preprocessing)
- **Smarter YAML Heuristics**: Reduced false positives (e.g., Python dict strings are no longer misclassified as YAML)
- **Temporal Ordering**: Built-in support for temporal ordering of content claims
- **Modular Architecture**: Extensible design with pluggable components
- **Type Safety**: Built with Python type hints and Pydantic models
- **Async Support**: Asynchronous API for improved performance

## 🚀 Getting Started

### Database Inspection

MCard uses BLOB storage for optimal performance and data integrity. The binary format allows for efficient storage and retrieval while MCard handles all necessary text conversions. To inspect the database:

```bash
# Open the database in SQLite CLI
sqlite3 mcard.db

# View the schema
.schema

# View binary content (first 20 bytes as hex)
SELECT hash, hex(substr(content, 1, 20)) as preview, g_time FROM card LIMIT 5;

# MCard's API provides easy access to content in various formats:
# - get_content() - Returns raw bytes for maximum performance
# - get_content(as_text=True) - Returns decoded text when needed
# - to_dict() - Automatically converts content to appropriate formats
```

### Prerequisites

- Python 3.9 or higher
- [uv](https://github.com/astral-sh/uv) - A fast Python package installer and resolver

### Basic Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/xlp0/MCard_TDD.git
   cd MCard_TDD
   ```

2. Set up the Python environment using the provided script:
   ```bash
   ./activate_venv.sh
   ```
   This will:
   - Create a Python virtual environment if it doesn't exist
   - Activate the environment
   - Install all required dependencies

3. For development, install additional development dependencies:
   ```bash
   uv pip install -e ".[dev]"
   ```

### Optional Dependencies

MCard supports optional features that can be installed as extras:

- **XML Processing** - For better XML handling with lxml:
  ```bash
  uv pip install -e ".[xml]"
  ```

## 🏗️ Project Structure

```
MCard_TDD/
├── mcard/                    # Core Python package
│   ├── config/               # Configuration management
│   ├── engine/               # Database engine implementations
│   │   ├── base.py           # Base engine interface
│   │   └── sqlite_engine.py  # SQLite implementation
│   └── model/                # Data models and content handling
│       ├── card.py           # Core MCard implementation
│       ├── card_collection.py # Collections of MCards
│       ├── clm/              # Content Lifecycle Management
│       ├── detectors/        # Content type detectors
│       └── hash/             # Hashing implementations
│           └── algorithms/   # Hash algorithm implementations
├── data/                     # Data storage directories
│   ├── databases/            # Database files
│   ├── db/                   # Additional database files
│   ├── loaded_content/       # Processed content storage
│   └── test_content/         # Test content files
├── docs/                     # Documentation
│   └── to-do-plan/           # Project planning documents
├── examples/                 # Example scripts
├── tests/                    # Test suite
│   ├── data/                 # Test data
│   └── test_data/            # Additional test data
├── pyproject.toml            # Project configuration
└── README.md                 # This file
```

## 🚦 Quick Start

### Using the Python API

```python
from mcard import MCard, MCardUtility

# Initialize the utility
utility = MCardUtility()

# Create a new card
card = MCard(
    content={"message": "Hello, MCard!"},
    content_type="application/json"
)

# Store the card
await utility.store_card(card)


# Retrieve the card by hash
retrieved = await utility.get_card(card.hash_value)
print(retrieved.content)  # {"message": "Hello, MCard!"}
```

## 🧪 Running Tests

Run the test suite (with uv):

```bash
uv run pytest -q
```

For test coverage report:

```bash
uv run pytest --cov=mcard --cov-report=term-missing
```

## 🔍 Content Type Detection and Validation

- __Binary-first strategy__: `BinaryFirstStrategy` runs signature detection directly on raw bytes via `BinarySignatureDetector.detect_from_bytes()` to avoid corruption.
- __Text detection__: Falls back to text detectors only when no binary signature is recognized.
- __Validation registry__: `ValidationRegistry` dispatches to `BinaryValidator` or `TextValidator` depending on the detected MIME.
- __YAML detection__: `TextFormatDetector._is_yaml()` was refined to avoid misclassifying Python-like content as YAML.
- __Problematic bytes guard__: Optional env flag `MCARD_INTERPRETER_GUARD_PROBLEMATIC=1` treats certain pathological byte patterns as binary to prevent hangs.

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📚 Documentation

For more detailed documentation, please see the [docs](docs/) directory:

- [Card Collection Guide](docs/card_collection_guide.md)
- [Global Time Design](docs/design_g_time.md)
- [Test-Driven Development Guide](docs/tdd_guide.md)
- [Cubical Logic Model](docs/cubical_logic_model.md)

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of notable changes.

## 📧 Contact

### Version 0.1.22 (2025-08-18)
- Robust file handling for pathological long-line files via streamed text normalization with adaptive soft wrapping.
- Environment-configurable tunables:
  - `MCARD_WRAP_WIDTH_DEFAULT` (default 1000)
  - `MCARD_WRAP_WIDTH_KNOWN` (default 1200)
  - `MCARD_MAX_PROBLEM_TEXT_BYTES` (default 2MB)
  - `MCARD_READ_TIMEOUT_SECS` (default 30)
- Captures original bytes metadata for normalized files: `original_size` and `original_sha256_prefix`.
- `metadata_only` mode for problematic files to record metadata without storing normalized content.
- `load_file_to_collection(...)` updated to plumb `metadata_only` flag; problematic files are streamed as safe text by default with fall back to capped binary if streaming fails.
- Linter cleanup in `mcard/config/env_parameters.py` (logger initialization after imports).

### Version 0.1.21 (2025-08-18)
- Binary-first content detection: raw-byte signature matching via `BinarySignatureDetector.detect_from_bytes()`; avoids text-decoding corruption.
- Fixes for misclassification of PNG/JPEG/GIF/PDF/ZIP(OpenXML)/RIFF; improved accuracy and stability.
- Refined YAML heuristics in `TextFormatDetector._is_yaml()` to reduce Python-dict false positives.
- Validation hardened: correct routing to `BinaryValidator`/`TextValidator`; truncated binaries are rejected.
- Optional safety guard: set `MCARD_INTERPRETER_GUARD_PROBLEMATIC=1` to treat pathological byte streams as binary.
- Test status: 135 tests passing on 2025-08-18.
- Latest commit: `a0c1400` - Added latest updates.

### Version 0.1.20 (2025-08-18)

#### Feature: Safe Fallback for Problematic Files
- Added opt-in fallback to safely load problematic files (e.g., extremely large single-line text or unstructured binaries).
- When enabled, files are read as capped binary BLOBs without decoding to avoid hangs/crashes.
- Default remains unchanged: problematic files are skipped unless explicitly included.

#### API Updates
- `mcard.file_utility.load_file_to_collection(path, collection, recursive=False, include_problematic=False, max_bytes_on_problem=2*1024*1024)`
  - `include_problematic=True` to include files detected as problematic.
  - `max_bytes_on_problem` caps bytes read during fallback (default 2MB).

#### Bug Fixes
- Restored `@classmethod` on `FileUtility._process_file(...)` to fix invocation errors introduced by an incorrect `@staticmethod` change.
- All tests pass.

#### Content Type Detection and Validation Fixes
- Binary detection now operates on raw bytes (no intermediate UTF-8 decoding), fixing PNG misclassification.
- More reliable detection for PNG/JPEG/GIF/PDF/ZIP/OpenXML and RIFF container formats.
- YAML detection heuristics tightened to avoid classifying Python dict-like text as YAML.
- Validation hardened: binary content no longer passes through text validators; truncated binaries are rejected.
- Test suite updated; as of 2025-08-18, 135 tests pass.

#### Environment Guard (Optional)
- Set `MCARD_INTERPRETER_GUARD_PROBLEMATIC=1` to treat pathological byte streams as binary to protect against timeouts/hangs.

---

### Version 0.1.17 (2025-07-04)

#### Database Storage Improvements
- Optimized BLOB storage for better performance
- Enhanced content handling with improved text conversion
- Updated documentation for clarity on binary storage and text access

---

### Version 0.1.16 (2025-07-01)

#### Content Preview Fix
- Fixed an issue in the file content preview functionality where content was not being displayed in the processed files summary
- Enhanced the `print_summary` function to fetch and display actual content from the CardCollection using the MCard hash
- Improved content preview generation to handle both direct content and content fetched from the collection
- Updated the example script to properly pass the CardCollection to the summary function
- Added better error handling for content retrieval and display

### Version 0.1.15 (2025-06-30)

#### Hash Algorithm Fix
- Fixed and stabilized the default hash algorithm setup to ensure consistent use of SHA-256
- Enhanced hash algorithm selection and validation to prevent unintentional algorithm switching
- Improved environment variable handling for hash algorithm configuration

### Version 0.1.12 (2024-06-16)

#### Dependency Updates and Fixes
- Updated `python-json-logger` to version 3.3.0 to resolve dependency conflicts
- Updated `python-dotenv` to version 1.1.0 for improved environment variable handling
- Updated `python-dateutil` to version 2.9.0.post0 for better date/time handling
- Added `pytest-asyncio` as a development dependency for proper async test support

#### Bug Fixes
- Fixed a warning about unknown `asyncio_mode` in pytest configuration
- Resolved several dependency conflicts to ensure stable builds
- Improved dependency resolution with `uv` for faster and more reliable package management

### Version 0.1.11 (2024-06-10)

#### DuckDB Removal
- Removed DuckDB as a supported database backend to simplify the codebase and dependencies
- SQLite is now the only supported database engine
- Updated all examples and documentation to reflect this change
- Removed DuckDB-related code and dependencies

### Package Management
- Switched to `uv` as the package manager for faster and more reliable dependency resolution
- Updated installation instructions to use `uv`
- Simplified dependency management with `pyproject.toml`

### Bug Fixes

#### Critical: Database Initialization (2024-06-10)

Fixed a critical issue in the SQLite database initialization that was causing data loss. Previously, the database would be recreated and all data would be lost every time the application started. The fix ensures that:

- Existing databases are preserved between application restarts
- The database schema is only created if it doesn't already exist
- All existing data remains intact during application updates

This change is particularly important for production deployments where data persistence is crucial. The fix was implemented in the `SQLiteConnection.setup_database()` method, which now properly checks for existing tables before attempting to create them.

### Database Schema Cleanup (2024-06-10)

Removed the unused `file_type` field from the database schema to improve efficiency and maintainability. The change includes:

- Removed `file_type` column from the `card` table schema
- Verified that no existing code was using this field
- All tests continue to pass with the simplified schema

This change makes the database more efficient by removing unused storage and simplifying the schema. The schema now only contains the essential fields: `hash`, `content`, and `g_time`.

## 📚 Documentation

For more detailed documentation, please see the [docs](docs/) directory:

- [Card Collection Guide](docs/card_collection_guide.md)
- [Global Time Design](docs/design_g_time.md)
- [Test-Driven Development Guide](docs/tdd_guide.md)
- [Cubical Logic Model](docs/cubical_logic_model.md)

### Version 0.1.12 (2024-06-16)

#### Dependency Updates and Fixes
- Updated `python-json-logger` to version 3.3.0 to resolve dependency conflicts
- Updated `python-dotenv` to version 1.1.0 for improved environment variable handling
- Updated `python-dateutil` to version 2.9.0.post0 for better date/time handling
- Added `pytest-asyncio` as a development dependency for proper async test support

#### Bug Fixes
- Fixed a warning about unknown `asyncio_mode` in pytest configuration
- Resolved several dependency conflicts to ensure stable builds
- Improved dependency resolution with `uv` for faster and more reliable package management

### Version 0.1.11 (2024-06-10)

#### DuckDB Removal
- Removed DuckDB as a supported database backend to simplify the codebase and dependencies
- SQLite is now the only supported database engine
- Updated all examples and documentation to reflect this change
- Removed DuckDB-related code and dependencies

### Package Management
- Switched to `uv` as the package manager for faster and more reliable dependency resolution
- Updated installation instructions to use `uv`
- Simplified dependency management with `pyproject.toml`

### Bug Fixes

#### Critical: Database Initialization (2024-06-10)

Fixed a critical issue in the SQLite database initialization that was causing data loss. Previously, the database would be recreated and all data would be lost every time the application started. The fix ensures that:

- Existing databases are preserved between application restarts
- The database schema is only created if it doesn't already exist
- All existing data remains intact during application updates

This change is particularly important for production deployments where data persistence is crucial. The fix was implemented in the `SQLiteConnection.setup_database()` method, which now properly checks for existing tables before attempting to create them.

### Database Schema Cleanup (2024-06-10)

Removed the unused `file_type` field from the database schema to improve efficiency and maintainability. The change includes:

- Removed `file_type` column from the `card` table schema
- Verified that no existing code was using this field
- All tests continue to pass with the simplified schema

This change makes the database more efficient by removing unused storage and simplifying the schema. The schema now only contains the essential fields: `hash`, `content`, and `g_time`.

## Documentation

- [Card Collection Guide](docs/card_collection_guide.md): Detailed guide on MCard collection management and hash collision handling
- [Global Time Design](docs/design_g_time.md): Documentation on the global time (`g_time`) implementation
- [Test-Driven Development Guide](docs/tdd_guide.md): Guide on our TDD approach and methodology

## Core Concepts

MCard implements an algebraically closed system where:
1. Every MCard is uniquely identified by its content hash (consistently using SHA-256 by default, with other algorithms configurable).
2. Every MCard has an associated claim time (timezone-aware timestamp with microsecond precision).
3. The database maintains these invariants automatically.
4. Content integrity is guaranteed through immutable hashes.
5. Temporal ordering is preserved at microsecond precision.

This design provides several key guarantees:
- **Content Integrity**: The content hash serves as both identifier and verification mechanism.
- **Temporal Signature**: All cards are associated with a timestamp: `g_time`.
- **Precedence Verification**: The claim time enables determination of content presentation order.
- **Algebraic Closure**: Any operation on MCards produces results that maintain these properties.
- **Type Safety**: Built on Pydantic with strict validation and type checking.

### Required Attributes for Each MCard

Each MCard **must** have the following three required attributes:

#### 1. **`content`**: The actual data being stored (string or bytes).
#### 2. **`hash`**: A cryptographic hash of the content, using SHA-256 by default (configurable to other algorithms).
#### 3. **`g_time`**: A timezone-aware timestamp with microsecond precision, representing the global time when the card was claimed.

## Directory Structure

- `mcard/`: Contains the main application code.
  - `algorithms/`: Hash algorithm implementations (renamed from `hash_algorithms`)
  - `engine/`: Database engines (SQLite, DuckDB)
  - `model/`: Core data models
  - `api.py`: FastAPI endpoints
  - `logging_config.py`: Logging configuration
- `examples/`: Example scripts demonstrating how to use the MCard system.
- `tests/`: Contains test files for the application.
  - `persistence/`: Database persistence tests
  - `unit/`: Unit tests
- `logs/`: Contains log files generated by the application.
- `data/db/`: Directory for storing database files used by the application.
- `data/files/`: Directory reserved for storing general files used by the application.
- `data/test_content/`: Test files of various types for content detection and validation.
- `data/loaded_content/`: Output directory for loaded and processed content (now gitignored).
- `docs/`: Project documentation.

## Database Technologies

We will be using embedded database technologies, such as SQLite, DuckDB, and LanceDB initially, to provide efficient and reliable data storage solutions for MCard. These technologies are well-suited for handling the requirements of content-addressable storage and will allow for easy integration and management of data within the application.

## Examples

### Default MCard API Example: `examples/MCard_Demo.py`

This script demonstrates the simplest way to use the MCard API through the `default_utility` interface. It covers:

- Adding new cards (with plain text or dictionaries, which are auto-converted to JSON)
- Retrieving cards by hash
- Searching for cards by content
- Counting the total number of cards in the collection

#### How to Run the Demo

```bash
python examples/MCard_Demo.py
```

#### Key Features
- **Minimal Setup**: Uses `from mcard import default_utility` for immediate access to core functionality.
- **Add and Retrieve**: Shows how to add cards and retrieve them by hash.
- **Search**: Demonstrates searching for cards containing a specific substring.
- **Summary Output**: Prints the total number of cards and search results.

---

### Modular Content Loader Example: `examples/Content_Loader.py`

This script demonstrates how to use the MCard system's content detection and storage features in a modular, easy-to-understand way. It:

- Loads files from `data/test_content/` (supports both text and binary types)
- Uses the `ContentTypeInterpreter` to detect file types and validate content
- Creates MCards for each file, handling text and binary content appropriately
- Saves processed files to `data/loaded_content/` with unique, type-appropriate filenames
- Prints summaries of processed files and cleans up temporary files

#### How to Run the Example

```bash
python examples/Content_Loader.py
```

#### Key Features of the Example
- **Modular Functions**: The script is organized into clear, single-purpose functions (e.g., `load_test_files`, `create_mcard_for_file`, `save_card_to_file`, etc.) for maintainability and extensibility.
- **Automatic Content Type Detection**: Uses file signatures and content validation to determine file type and extension.
- **Binary and Text Handling**: Handles binary files (e.g., images) and text files differently, ensuring correct storage and retrieval.
- **Output Directory**: All processed content is saved to `data/loaded_content/` (which is now gitignored).
- **Temporary File Cleanup**: Removes temporary binary files after processing.

See the script and its docstrings for further details and customization options.

### Handling Problematic Files (very large/single-line)

Some files can be pathological (e.g., extremely large single-line text or unstructured binaries). The loader now safely handles these via streamed text normalization with adaptive soft wrapping and strict byte/time caps.

- Defaults remain safe: problematic files are skipped unless `include_problematic=True`.
- When included, problematic files are processed as normalized text with UTF-8 replacement and soft wraps on-the-fly.
- If streaming fails unexpectedly, the system falls back to a capped binary BLOB read.
- Metadata captured for normalized files includes `original_size` and `original_sha256_prefix`.

Example using `load_file_to_collection()` from `mcard.file_utility`:

```python
from pathlib import Path
from mcard.model.card_collection import CardCollection
from mcard.file_utility import load_file_to_collection

collection = CardCollection()

# Load a single file with safe streamed normalization (and optional metadata-only mode)
results = load_file_to_collection(
    Path("tests/test_data/OneMoreLongStringFile.js"),
    collection,
    include_problematic=True,             # opt-in to include problematic files
    max_bytes_on_problem=2 * 1024 * 1024, # cap for streaming/fallback paths
    metadata_only=False                   # set True to store only metadata for problematic files
)

# Or load a directory recursively with the same options
results = load_file_to_collection(
    Path("tests/test_data"),
    collection,
    recursive=True,
    include_problematic=True,
    max_bytes_on_problem=2 * 1024 * 1024,
    metadata_only=False
)
```

Notes:

- Normalized text is stored with `mime_type='text/plain'` and includes `normalized=True` and `wrap_width` in the file info.
- When fallback occurs, MIME is `application/octet-stream` and only capped bytes are stored.
- Adaptive wrap width is chosen by extension via env-configured values.

Environment variables to tune behavior:

- `MCARD_WRAP_WIDTH_DEFAULT` (default 1000)
- `MCARD_WRAP_WIDTH_KNOWN` (default 1200)
- `MCARD_MAX_PROBLEM_TEXT_BYTES` (default 2MB)
- `MCARD_READ_TIMEOUT_SECS` (default 30)


## .gitignore Notes

- The `data/loaded_content/` directory is now included in `.gitignore` and will not be tracked by git. This ensures that output/generated files do not pollute the repository.

## PyTest Configuration

- The project uses [PyTest](https://docs.pytest.org/en/stable/) for testing.
- Tests are located in the `tests` directory.
- The configuration file `pytest.ini` specifies test paths and naming conventions.

## Logging Configuration

-- The project uses Python's built-in `logging` with a centralized configuration in `mcard/config/logging_config.py`.
-- Logs are written to `logs/mcard.log` using a rotating file handler (max 10MB, 5 backups).
-- The logging format includes timestamp, logger name, level, and message.
-- Logging is not configured on import. Entry points (your scripts, CLIs, apps, tests) should explicitly call `setup_logging()` once at startup.
-- Log levels are environment-driven via `MCARD_SERVICE_LOG_LEVEL` (default `DEBUG`). The package logger `mcard` defaults to `INFO`, the root logger defaults to `WARNING`.

### Usage

```python
from mcard.config.logging_config import setup_logging
import logging

def main():
    setup_logging()  # configure console + rotating file handlers
    logger = logging.getLogger(__name__)
    logger.info("MCard app started")

if __name__ == "__main__":
    main()
```

### Environment variables

- `MCARD_SERVICE_LOG_LEVEL` (e.g., `DEBUG`, `INFO`) controls handler levels.
- Logs directory: `logs/` at the project root. The file name is `mcard.log`.

Notes:
- `run_mcard.py` demonstrates calling `setup_logging()` explicitly.
- For library modules, use `logging.getLogger(__name__)` and avoid configuring logging in module scope.

## Running Tests

To run tests (with uv):
```bash
uv run pytest -q
```

To run tests with coverage:
```bash
uv run pytest --cov=mcard
```

## Hegel's Dialectic in Testing and CI/CD

Hegel's dialectic is a philosophical framework that describes the process of development and change through a triadic structure: thesis, antithesis, and synthesis. Here's how it relates to software testing and Continuous Integration/Continuous Deployment (CI/CD):

1. **Thesis (Initial Code)**: Represents the initial code or feature implementation, the starting point where a developer writes code to fulfill a specific requirement or feature.

2. **Antithesis (Testing and Bugs)**: Arises during the testing phase, where tests are executed. If tests fail or bugs are discovered, they represent a challenge to the initial implementation, highlighting discrepancies between intended functionality and actual behavior.

3. **Synthesis (Refinement and Improvement)**: Occurs when developers address the issues identified during testing, leading to a refined version of the code that resolves conflicts between the initial implementation and testing outcomes.

### CI/CD Integration
In a CI/CD pipeline, this dialectical process is continuous:

- **Continuous Integration**: Developers frequently integrate code changes into a shared repository. Each integration triggers automated tests, allowing for rapid identification of issues against the current codebase.

- **Continuous Deployment**: Once the code passes testing, it can be automatically deployed, representing the synthesis where refined code is made available to users.

This iterative process fosters continuous improvement, where each round of testing and deployment leads to better software quality and functionality. By applying Hegel's dialectic, teams can embrace the idea that conflict (in the form of bugs and failures) is a natural and necessary part of the development process, ultimately leading to a more robust and effective product.

## Handling Duplicate Events

When a duplicate card is detected, the `duplicate_event_card` is assigned a new timestamp value. This ensures that even though the content is identical to the original card, the hash value will be unique due to the different timestamp. This mechanism allows for robust handling of duplicate content while maintaining the integrity of the system.

## MD5 Collision Testing

The test suite includes verification of MD5 collision detection using known collision pairs from the FastColl attack. These pairs produce identical MD5 hashes despite having different content:

### MD5 Collision Pair
```
Input 1:
4dc968ff0ee35c209572d4777b721587d36fa7b21bdc56b74a3dc0783e7b9518afbfa200a8284bf36e8e4b55b35f427593d849676da0d1555d8360fb5f07fea2
                                                                     ^^^                                    ^^^

Input 2:
4dc968ff0ee35c209572d4777b721587d36fa7b21bdc56b74a3dc0783e7b9518afbfa202a8284bf36e8e4b55b35f427593d849676da0d1d55d8360fb5f07fea2
                                                                     ^^^                                    ^^^
```

Key differences:
1. `200` vs `202`
2. `d15` vs `d1d`

Both inputs produce the same MD5 hash value, demonstrating MD5's vulnerability to collision attacks. This is why MCard defaults to using more secure hash functions like SHA-256.

## Testing Behavior

The current tests, particularly `@test_sqlite_persistence.py`, will always clear the database after one of the test functions is run. This means that `test_mcard.db` will only contain the data from the last test executed. If the `clear()` function in the fixture is uncommented, it will remove the content of the last test as well.

## Core Dependencies

- `SQLAlchemy==1.4.47`: SQL toolkit and ORM
- `aiosqlite==0.17.0`: Async SQLite database driver
- `python-dateutil==2.8.2`: Date/time utilities
- `python-dotenv==1.0.0`: Environment management

## Description
MCard is a project designed to facilitate card management with a focus on validation and logging features.

## Installation

### Using uv

You can install the MCard package from PyPI (once published):

```bash
uv pip install mcard
```

### Installing from source

To install MCard directly from the source code:

```bash
# Clone the repository
git clone https://github.com/yourusername/MCard_TDD.git
cd MCard_TDD

# Install in development mode with uv
uv pip install -e .

# Install with development dependencies
uv pip install -e ".[dev]"
```

### Development Environment Setup

1. Set up a virtual environment using uv:
```bash
# Simply run the activate script which handles uv setup
source activate_venv.sh
```

This script will:
- Ensure conda is disabled (if present)
- Create a virtual environment using uv if it doesn't exist
- Activate the virtual environment
- Install dependencies from pyproject.toml using uv

Alternatively, you can manually set up the environment:
```bash
# Create and activate virtual environment with uv
uv venv .venv
source .venv/bin/activate

# Install dependencies with uv
uv pip sync pyproject.toml
```

## Usage

After installation, you can use MCard in your Python code:

```python
from mcard.model.card import MCard
from mcard.model.card_collection import CardCollection

# Create a new card
card = MCard(content="Hello, MCard!")

# Create a card collection
collection = CardCollection()

# Add the card to the collection
collection.add(card)

# Retrieve the card by its hash
retrieved_card = collection.get_by_hash(card.hash)
print(retrieved_card.content)  # Outputs: Hello, MCard!
```


# Or use the installed command-line entry point
mcard
```

## Recent Updates

### MCard Detail View Component
- Created a new component `mcard_detail_view.html` to display detailed information about MCards, including:
  - Full hash string
  - g_time string
  - Content type
  - Appropriate content display for images, videos, PDFs, and plain text.

### Dynamic Content Loading
- Implemented functionality to dynamically load and display card details when a card entry is clicked.
- Added JavaScript functions to handle click events and fetch card details from the server.

### Error Handling and Logging
- Enhanced error handling in the Flask backend to log errors and provide better feedback.
- Added detailed logging in the JavaScript to track the fetching and rendering process.

### Template Updates
- Updated existing templates to integrate the new detail view component and ensure proper rendering.

### User Experience Improvements
- Improved visual feedback for selected cards.
- Ensured that the focused area updates correctly without becoming blank.

### Configuration Management Refactoring (2024-12-18)
- Renamed `EnvConfig` to `EnvParameters` for better clarity and consistency
- Moved configuration management from `env_config.py` to `env_parameters.py`
- Updated all references to use the new class name across the codebase
- Enhanced test coverage for configuration parameters
- Maintained singleton pattern for configuration management
- Ensured backward compatibility with existing environment variable handling

### Database Enhancements
- Implemented `get_all()` method in SQLiteEngine for efficient pagination
- Added support for page size and page number parameters
- Enhanced error handling for invalid pagination parameters
- Improved performance by optimizing SQL queries
- Added comprehensive test coverage for pagination functionality

## Recent Changes

### Directory Structure Updates
- The `hash_algorithms` directory has been renamed to `algorithms` for simplicity and clarity.
- The `hash_validator.py` file has been renamed to `validator.py` to simplify the naming convention.

### Updated Imports
- All relevant import statements across the codebase have been updated to reflect the new structure and naming.

### Engine Refactor
- Removed the abstract `search_by_content` method from `SQLiteEngine` and `DuckDBEngine`.
- Integrated search functionality into the [search_by_string](cci:1://file:///mcard/model/card_collection.py:94:4-96:82) method, allowing searches across content, hash, and g_time fields.

### Event Generation
- Updated [generate_duplication_event](cci:1://file:///mcard/model/event_producer.py:38:0-54:28) and [generate_collision_event](cci:1://file:///mcard/model/event_producer.py:57:0-76:38) to return JSON strings.
- Enhanced event structure to include upgraded hash functions and content size.

### Logging
- Integrated logging into test cases for better traceability and debugging.

### MCard Class Update
- The [MCard](cci:2://file:///mcard/model/card.py:6:0-47:9) constructor now accepts a [hash_function](cci:1://file:///mcard/model/event_producer.py:8:0-23:16) parameter, providing more flexibility in hash generation.

### Tests
- Adjusted tests to verify the new event generation logic and ensure search functionality works as intended.

## Centralized Configuration Management

### Overview
MCard has adopted a centralized configuration management approach to improve maintainability, scalability, and readability. This involves consolidating all configuration constants into a single location, making it easier to manage and update configuration values across the application.

### Configuration Constants
All configuration constants are now defined in `config_constants.py`. This file contains named constants for various configuration values, including:

- Database schema and paths
- Hash algorithm constants and hierarchy
- Environment variable names
- API configuration
- HTTP status codes
- Error messages
- Event types and structure

### Benefits
Centralized configuration management provides several benefits, including:

- **Single Source of Truth**: All configuration constants are managed in one location.
- **Type Safety**: Constants are properly typed and documented.
- **Maintainability**: Changes to configuration values only need to be made in one place.
- **Code Completion**: IDE support for constant names improves developer productivity.
- **Documentation**: Each constant group is documented with its purpose and usage.
- **Testing**: Test files use the same constants as production code, ensuring consistency.

### Implementation
The `config_constants.py` file uses an enum-based approach for hash algorithms, ensuring type safety and readability. The file is organized into logical groups, making it easier to find and update specific configuration values.

### Example Usage
To use a configuration constant, simply import the `config_constants` module and access the desired constant. For example:
```python
from config_constants import HASH_ALGORITHM_SHA256

# Use the SHA-256 hash algorithm
hash_algorithm = HASH_ALGORITHM_SHA256
```
By adopting a centralized configuration management approach, MCard has improved its maintainability, scalability, and readability, making it easier to manage and update configuration values across the application.

## Using MCardFromData for Stored Values

When retrieving stored MCard data from the database, always use the subclass `MCardFromData`. This approach allows you to bypass unnecessary and unwanted algorithms, significantly speeding up the MCard instantiation process.

## Project Structure

```plaintext
MCard_TDD/
├── mcard/
│   ├── algorithms/          # Hash algorithm implementations
│   ├── engine/             # Database engines (SQLite, DuckDB)
│   ├── model/              # Core data models
│   ├── api.py             # FastAPI endpoints
│   └── logging_config.py   # Logging configuration
├── tests/
│   ├── persistence/       # Database persistence tests
│   └── unit/             # Unit tests
├── docs/                  # Project documentation
├── data/
│   ├── db/               # Database files
│   └── files/            # General files
└── logs/                 # Application logs
```
## Configuration
### Environment Setup
Create a .env file with the following variables:

```plaintext
MCARD_DB_PATH=data/db/mcard_demo.db
TEST_DB_PATH=data/db/test_mcard.db
MCARD_SERVICE_LOG_LEVEL=DEBUG
 ```

## Development Guidelines
### Using MCardFromData
When retrieving stored data, use MCardFromData instead of the base MCard class:

```python
from mcard.model.card import MCardFromData

stored_card = MCardFromData(content=content, hash=hash, g_time=g_time)
 ```

### Hash Algorithm Configuration
The default hash algorithm is SHA-256, but it's configurable:
```python
from mcard.algorithms import HASH_ALGORITHM_SHA256
 ```

## Installation

To set up the project, follow these steps:

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```

2. Activate the virtual environment:
   - On macOS and Linux:
     ```bash
     source .venv/bin/activate
     ```
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```

3. Configure your environment:
   - Copy `.env.example` to create your own `.env` file.
   - The default configuration uses:
     - Database path: `data/db/mcard_demo.db`.
     - Hash algorithm: SHA-256.
     - Connection pool size: 5.
     - Connection timeout: 30 seconds.

## Directory Structure

- **mcard/**
  - **engine/**: Contains the database engine implementations, currently only SQLite.
  - **model/**: Contains the core data models, including `MCard`.
  - **tests/**: Contains all test cases for the MCard library, ensuring functionality and correctness.

## SQLite Persistence Testing

- **tests/persistence/sqlite_test.py**: Contains test cases for SQLite persistence, ensuring data integrity and consistency.

The tests in `@test_sqlite_persistence.py` are designed to clear the database after each test function is run. This means that the `test_mcard.db` file will only contain the data from the last test executed. If the `clear()` function in the fixture is uncommented, it will remove the content of the last test as well. This behavior is intended to ensure that each test starts with a clean database, allowing for more accurate and reliable testing results.
