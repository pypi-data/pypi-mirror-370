#!/usr/bin/env python3

import warnings
from urllib3.exceptions import NotOpenSSLWarning

# Must filter BEFORE requests/urllib3 are imported
warnings.simplefilter("ignore", NotOpenSSLWarning)

import argparse
import sys

from .cmdmate_client import cmdmateClient


def main():
    parser = argparse.ArgumentParser(description="cmdmate - Your AI powered terminal assistant 🚀")
    parser.add_argument("query", type=str, help="The command or task you want to perform")
    parser.add_argument("-o", "--os", type=str, help="Target OS (auto-detected if not provided)")
    # parser.add_argument("--server", type=str, default="http://127.0.0.1:8000/", help="Server URL")
    parser.add_argument("--server", type=str, default="https://cmdmate.onrender.com/", help="Server URL")
    args = parser.parse_args()

     # --- OS aliases ---
    os_aliases = {
        "win": "windows",
        "windows": "windows",
        "lin": "linux",
        "linux": "linux",
        "mac": "mac",
        "darwin": "mac"
    }

    if args.os:
        os_name = os_aliases.get(args.os.lower(), args.os.lower())
    else:
        os_name = None  # let get_command auto-detect

    client = cmdmateClient(args.server)
    try:
        command = client.get_command(args.query, os_name)
        print(command)
    except RuntimeError as e:
        print(e, file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
