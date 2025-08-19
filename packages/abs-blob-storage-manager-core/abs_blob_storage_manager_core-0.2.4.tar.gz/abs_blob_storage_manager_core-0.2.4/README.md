# Blob Storage Manager Core

A flexible and extensible core library for managing blob storage operations across various cloud providers and local storage systems.

## Features

- Unified interface for blob storage operations
- Support for multiple cloud providers
- Local storage system support
- Asynchronous operations
- Type-safe operations with Pydantic models
- FastAPI integration

## Installation

```bash
pip install blob-storage-manager-core
```

## Quick Start

```python
from blob_storage_manager_core import BlobStorageManager

# Initialize with your preferred storage provider
storage_manager = BlobStorageManager(
    provider="local",  # or "aws", "azure", "gcp"
    config={
        "base_path": "/path/to/storage"  # Provider-specific configuration
    }
)

# Upload a file
async def upload_file():
    with open("example.txt", "rb") as f:
        await storage_manager.upload(
            file=f,
            destination="path/to/upload/example.txt"
        )

# Download a file
async def download_file():
    file_content = await storage_manager.download(
        source="path/to/download/example.txt"
    )
    with open("downloaded.txt", "wb") as f:
        f.write(file_content)
```

## Supported Providers

- Azure Blob Storage

## Configuration

### Azure Blob Storage
```python
config = {
    "connection_string": "your_connection_string",
    "container_name": "your-container"
}
```

## API Reference

### Core Methods

- `upload(file: BinaryIO, destination: str)`: Upload a file to storage
- `download(source: str)`: Download a file from storage
- `delete(path: str)`: Delete a file from storage
- `list_files(prefix: str)`: List files in storage
- `get_file_info(path: str)`: Get metadata for a file

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, email info@autobridgesystems.com or open an issue in the repository.
