"""
Command line interface for Atlas AWS Auto Download.
"""

import argparse
import sys
from .core import aws_download


def main():
    """Main entry point for the command line interface."""
    
    logo = r'''   

          _   _             ____  _       _        __
     /\  | | | |           |  _ \(_)     (_)      / _|
    /  \ | |_| | __ _ ___  | |_) |_  ___  _ _ __ | |_ ___
   / /\ \| __| |/ _` / __| |  _ <| |/ _ \| | '_ \|  _/ _ \
  / ____ \ |_| | (_| \__ \ | |_) | | (_) | | | | | || (_) |
 /_/    \_\__|_|\__,_|___/ |____/|_|\___/|_|_| |_|_| \___/

        `-:-.   ,-;"`-:-.   ,-;"`-:-.   ,-;"`-:-.   ,-;"
        `=`,'=/     `=`,'=/     `=`,'=/     `=`,'=/
            y==/        y==/        y==/        y==/
        ,=,-<=`.    ,=,-<=`.    ,=,-<=`.    ,=,-<=`.
        ,-'-'   `-=_,-'-'   `-=_,-'-'   `-=_,-'-'   `-=_
                    
    '''

    description_text = f'''{logo} 
        This script is used to download files from AWS S3 bucket.
        The configuration file should be in the following format:
            Project:***
            Alias ID:***
            S3 Bucket:***
            Account:***
            Password:***
            Region:***
            Aws_access_key_id:***
            Aws_secret_access_key:***
        .'''
    
    parser = argparse.ArgumentParser(
        description=description_text, 
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "config", 
        help="Configuration file path"
    )
    parser.add_argument(
        "-o", "--output", 
        help="Output directory to save the downloaded files", 
        default='./'
    )

    args = parser.parse_args()

    config_file = args.config
    local_path = args.output

    try:
        aws_download(config_file, local_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
