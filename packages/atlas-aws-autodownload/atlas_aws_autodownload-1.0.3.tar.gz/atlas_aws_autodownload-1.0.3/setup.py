from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="atlas-aws-autodownload",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python tool for downloading files from AWS S3 bucket with configuration file support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/atlas-aws-autodownload",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Archiving :: Backup",
    ],
    python_requires=">=3.7",
    install_requires=[
        "boto3>=1.26.0",
        "tqdm>=4.64.0",
    ],
    entry_points={
        "console_scripts": [
            "atlas-aws-download=atlas_aws_autodownload.cli:main",
        ],
    },
    keywords="aws, s3, download, boto3, atlas",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/atlas-aws-autodownload/issues",
        "Source": "https://github.com/yourusername/atlas-aws-autodownload",
    },
)
