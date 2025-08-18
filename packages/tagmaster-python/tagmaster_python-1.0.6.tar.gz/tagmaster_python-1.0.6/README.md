# Tagmaster Python Client

A comprehensive Python client library for the Tagmaster classification API.

## 🚀 Features

- **🔑 API Key Authentication**: Simple authentication using project-specific API keys
- **📁 Project Management**: Full CRUD operations for projects
- **🏷️ Category Management**: Create, update, delete, and manage classification categories
- **🤖 AI Classification**: Text and image classification with confidence scoring
- **📊 Analytics & History**: Comprehensive classification history and statistics
- **📁 CSV Import/Export**: Bulk operations for categories and classification data
- **🔧 Utility Functions**: Health checks, connection testing, and configuration

## 📖 Documentation

For comprehensive documentation, examples, and API reference, see [README_PYTHON_CLIENT.md](README_PYTHON_CLIENT.md).

## Quick Install

```bash
pip install tagmaster-python
```

## Quick Start

```python
from tagmaster import TagmasterClassificationClient
import json

# Initialize the client
client = TagmasterClassificationClient(api_key="your-api-key-here")

# Classify text
result = client.classify_text("Customer login issue")
print(json.dumps(result, indent=2))
```

## Documentation

See [README_PYTHON_CLIENT.md](README_PYTHON_CLIENT.md) for detailed documentation.

## Development

### Building the Package

```bash
python build_package.py
```

### Testing

```bash
python test_tagmaster.py
```

### Running Examples

```bash
python example_usage.py
```

## License

MIT License - see [LICENSE](LICENSE) for details. 