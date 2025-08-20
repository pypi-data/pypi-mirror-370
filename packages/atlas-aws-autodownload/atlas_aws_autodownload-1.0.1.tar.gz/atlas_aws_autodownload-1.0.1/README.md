# Atlas AWS Auto Download

A Python tool for downloading files from AWS S3 bucket with configuration file support.

## Features

- 🔐 **Secure**: Supports AWS access keys and region configuration
- 📁 **Flexible**: Configurable S3 bucket and folder paths
- 📝 **Logging**: Comprehensive logging of all download operations
- 🚀 **Progress**: Visual progress bars for download operations
- ⚙️ **Configurable**: Simple configuration file format

## Installation

### From PyPI (Recommended)

```bash
pip install atlas-aws-autodownload
```

### From Source

```bash
git clone https://github.com/yourusername/atlas-aws-autodownload.git
cd atlas-aws-autodownload
pip install -e .
```

## Usage

### Command Line Interface

After installation, you can use the `atlas-aws-download` command:

```bash
atlas-aws-download config.txt -o ./downloads
```

### Python API

```python
from atlas_aws_autodownload import aws_download

aws_download("config.txt", "./downloads")
```

## Configuration File Format

Create a configuration file with the following format:

```text
Project:MyProject
Alias ID:my-alias
S3 Bucket:my-bucket-name
Account:my-account
Password:my-password
Region:us-east-1
Aws_access_key_id:AKIAIOSFODNN7EXAMPLE
Aws_secret_access_key:wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

**Note**: The tool also supports `s3://` URI format in the configuration file.

## Requirements

- Python 3.7+
- boto3
- tqdm

## Development

### Setup Development Environment

```bash
git clone https://github.com/yourusername/atlas-aws-autodownload.git
cd atlas-aws-autodownload
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
black atlas_aws_autodownload/
```

### Type Checking

```bash
mypy atlas_aws_autodownload/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues or have questions, please:

1. Check the [Issues](https://github.com/yourusername/atlas-aws-autodownload/issues) page
2. Create a new issue if your problem isn't already reported
3. Contact the maintainers at your.email@example.com

## Changelog

### Version 1.0.0
- Initial release
- Basic S3 download functionality
- Configuration file support
- Command line interface
- Progress bars and logging
