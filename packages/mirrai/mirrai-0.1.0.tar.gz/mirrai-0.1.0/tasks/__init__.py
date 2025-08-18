"""
Makefile-like task automation for the Mirrai project.

This module provides cross-platform build automation using Python's invoke,
serving as a modern alternative to traditional Makefiles.

Tasks include:
- Building and formatting code
- Running tests and type checking
- Managing dependencies
- Cleaning build artifacts

Usage:
    invoke <task>          # Run a task
    invoke --list          # List all available tasks
    invoke <task> --help   # Get help for a specific task
"""

from .make import *
