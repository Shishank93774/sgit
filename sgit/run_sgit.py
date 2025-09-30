#!/usr/bin/env python3
"""
Entry point script for sgit - can be used for development without installation.
"""
import sys
import os

# Add the sgit package to the path
sys.path.insert(0, os.path.dirname(__file__))

from sgit.cli.main import main

if __name__ == "__main__":
    main()