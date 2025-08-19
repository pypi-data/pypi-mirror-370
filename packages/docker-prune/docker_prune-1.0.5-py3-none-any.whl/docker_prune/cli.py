#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Prune Docker Resources
This script provides commands to clean up unused Docker containers, images,
volumes, and networks. Each command includes filters to fine-tune the cleanup
process.
"""

from .main import (
    cli
)

if __name__ == '__main__':
    cli()
