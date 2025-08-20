"""
Atlas AWS Auto Download

A Python tool for downloading files from AWS S3 bucket with configuration file support.
"""

__version__ = "1.0.3"
__author__ = "Haopeng Yu"
__email__ = "hyu@atlasbioinfo.com"

from .core import aws_download

__all__ = ["aws_download"]
