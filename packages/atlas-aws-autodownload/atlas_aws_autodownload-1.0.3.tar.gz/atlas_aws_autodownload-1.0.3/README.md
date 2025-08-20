# Atlas AWS Auto Download

A Python tool for automatically downloading BGI sequencing data from AWS S3 bucket with configuration file support.

## Features

- 🔬 **BGI Specific**: Optimized for downloading BGI sequencing data from AWS S3
- 🔐 **Secure**: Supports AWS access keys and region configuration
- 📁 **Flexible**: Configurable S3 bucket and folder paths for different projects
- 📝 **Logging**: Comprehensive logging of all download operations
- 🚀 **Progress**: Visual progress bars for large sequencing data downloads
- ⚙️ **Configurable**: Simple configuration file format for BGI project settings
- 📊 **Batch Processing**: Efficiently handles multiple sequencing files and directories

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

After installation, you can use the `atlas-aws-download` command to download BGI sequencing data:

```bash
# Download to current directory
atlas-aws-download bgi_config.txt

# Download to specific directory
atlas-aws-download bgi_config.txt -o ./sequencing_data

# Download specific project data
atlas-aws-download project_config.txt -o ./projects/BGI_2024
```

### Command Line Help

```bash
$ atlas-aws-download -h
```

### Python API

```python
from atlas_aws_autodownload import aws_download

# Download BGI sequencing data
aws_download("bgi_config.txt", "./sequencing_data")

# Download specific project
aws_download("project_config.txt", "./projects/BGI_Project_2024")
```

## Configuration File Format

Create a configuration file with the following format for BGI sequencing data:

```text
Project:***
Alias ID:***
S3 Bucket:***
Account:***
Password:***
Region:***
Aws_access_key_id:***
Aws_secret_access_key:***
```

**Note**: 
- The tool also supports `s3://` URI format in the configuration file
- For BGI projects, typically use `ap-southeast-1` region (Singapore)
- Project names usually follow BGI naming conventions

**Note**: The tool also supports `s3://` URI format in the configuration file.

## Requirements

- Python 3.7+
- boto3 (for AWS S3 access)
- tqdm (for progress bars)

## Typical Use Cases

- **BGI Sequencing Data**: Download raw sequencing data from BGI's AWS S3 storage
- **Project Management**: Organize downloads by project, sample, or experiment
- **Batch Processing**: Handle multiple sequencing runs and data types
- **Data Transfer**: Efficiently transfer large sequencing datasets to local storage


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
