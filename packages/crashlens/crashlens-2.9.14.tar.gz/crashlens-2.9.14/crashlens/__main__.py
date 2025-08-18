#!/usr/bin/env python3
"""
CrashLens CLI Entry Point
Imports and runs the main CLI from cli.py to avoid code duplication.
"""

from .cli import cli

if __name__ == '__main__':
    cli()