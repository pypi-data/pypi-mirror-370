# OpenAPI Scanner

A tool for scanning and testing OpenAPI specifications.

## Features

- Support for both JSON and YAML OpenAPI specifications
- Flexible authentication system
- Automatic path parameter replacement
- Custom header support
- Multiple report formats (Console, HTML, CSV, JSONL)

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## Usage

### Basic Usage

```bash
# Using JSON specification
python -m specphp_scanner spec.json --host localhost --port 8080

# Using YAML specification
python -m specphp_scanner spec.yaml --host localhost --port 8080
```

### Using Authentication

```bash
# Using module path
python -m specphp_scanner spec.json --auth-class examples.koel.auth.KoelAuth --auth-params '{"email": "user@example.com", "password": "secret"}'

# Using file path
python -m specphp_scanner spec.json --auth-class ./examples/koel/auth.py --auth-params '{"email": "user@example.com", "password": "secret"}'
```

### Using Custom Headers

```bash
python -m specphp_scanner spec.json --headers '{"X-Custom-Header": "value"}'
```

### Generating Reports

```bash
# Console output (default)
python -m specphp_scanner spec.json

# HTML report
python -m specphp_scanner spec.json --format html --output report.html

# CSV report
python -m specphp_scanner spec.json --format csv --output report.csv

# JSONL report
python -m specphp_scanner spec.json --format jsonl --output report.jsonl
```

## Command Line Options

- `spec_file`: Path to OpenAPI specification file (JSON or YAML)
- `--host`: Target host (default: localhost)
- `--port`: Target port (default: 8080)
- `--auth-class`: Authentication class path or Python file path
- `--auth-params`: JSON string containing authentication parameters
- `--headers`: JSON string containing custom headers
- `--format`: Report format (console, html, csv, jsonl)
- `--output`: Output file path for the report
- `--verbose`, `-v`: Enable verbose logging

## Creating Custom Authentication Classes

Create a class that inherits from `BaseAuth`:

```python
from specphp_scanner.auth.base import BaseAuth

class MyCustomAuth(BaseAuth):
    def __init__(self, **kwargs):
        # Initialize your authentication parameters
        self.token = None

    def authenticate(self):
        # Implement your authentication logic
        # This method should be called before making API requests
        pass

    def get_headers(self):
        # Return headers required for authentication
        return {"Authorization": f"Bearer {self.token}"}

    def get_cookies(self):
        # Return cookies required for authentication
        return {}
```

## Examples

See the `examples` directory for sample implementations.

## Project Structure

```
specphp_scanner/
├── __init__.py
├── cli.py
├── scanner.py
├── auth/
│   ├── __init__.py
│   ├── base.py
│   └── factory.py
└── utils/
    ├── __init__.py
    ├── param_generator.py
    ├── report.py
    └── templates/
        └── report.html
```

## Running Tests

```bash
pytest
```
