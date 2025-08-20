"""
Core functionality for AWS S3 download operations.
"""

import os
import boto3
import tqdm
import logging
from typing import Optional


def aws_download(config_file: str, local_path: str) -> None:
    """
    Download files from AWS S3 bucket based on configuration file.
    
    Args:
        config_file: Path to the configuration file
        local_path: Local directory to save downloaded files
        
    Raises:
        ValueError: If required configuration parameters are missing
        FileNotFoundError: If configuration file doesn't exist
    """
    
    aws_access_key_id = ''
    aws_secret_access_key = ''
    region_name = ''
    bucket_name = ''
    folder_path = ''
    
    # Read configuration file
    with open(config_file, "r", encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.find("：") != -1:
                line = line.replace("：", ":")
            if line.startswith("Aws_access_key_id"):
                aws_access_key_id = line.split(":")[1].strip()
            if line.startswith("Aws_secret_access_key"):
                aws_secret_access_key = line.split(":")[1].strip()
            if line.startswith("Region"):
                region_name = line.split(":")[1].strip()
            if line.startswith("S3 Bucket"):
                bucket_name = line.split(":")[1].strip()
            # If s3:// format URI is found, use it preferentially
            if line.find("s3://") != -1:
                line = line.strip().split("s3://")[1]
                bucket_name = line.split("/")[0].strip()
                folder_path = line.split("/")[1].strip()

    # Validate required configuration parameters
    if not bucket_name:
        raise ValueError("Bucket name is required but not found in config file")
    if not aws_access_key_id:
        raise ValueError("AWS Access Key ID is required but not found in config file")
    if not aws_secret_access_key:
        raise ValueError("AWS Secret Access Key is required but not found in config file")
    if not region_name:
        raise ValueError("Region is required but not found in config file")
    
    # If no folder path is specified, use root directory
    if not folder_path:
        folder_path = ""

    # Print configuration information
    print(f'Configuration file: {config_file}')
    print(f'Region: {region_name}')
    print(f'Local path: {local_path}')
    print(f'Bucket name: {bucket_name}')
    print(f'Folder path: {folder_path}')
    print(f'AWS Access Key ID: {aws_access_key_id[:4]}...{aws_access_key_id[-4:]}')
    
    # Create local directory
    local_path = os.path.join(local_path, folder_path)
    os.makedirs(local_path, exist_ok=True)

    # Setup logging
    log_filename = os.path.join(local_path, f'{folder_path}.aws.log' if folder_path else 'aws.log')
    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    logging.info(f'Configuration file: {config_file}')
    logging.info(f'Local path: {local_path}')
    logging.info(f'Bucket name: {bucket_name}')
    logging.info(f'Folder path: {folder_path}')

    # Initialize S3 client
    s3 = boto3.client('s3', 
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    region_name=region_name)
    
    # List objects in S3 bucket
    objects = s3.list_objects(Bucket=bucket_name, Prefix=folder_path)
    logging.info(f'Objects: {objects}')

    if 'Contents' not in objects:
        logging.warning('No objects found in the specified folder')
        return

    # Download each object
    for obj in tqdm.tqdm(objects['Contents']):
        key = obj['Key']
        if not key.endswith('/'):
            local_file_path = os.path.join(local_path, os.path.relpath(key, folder_path))
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
            logging.info(f'Downloading: {key}')
            s3.download_file(bucket_name, key, local_file_path)
            logging.info(f'Downloaded: {local_file_path}')

    logging.info('Download completed')
