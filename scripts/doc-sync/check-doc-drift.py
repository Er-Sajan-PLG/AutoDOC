#!/usr/bin/env python3
"""AutoDOC drift entry point; see engine.py."""
import sys
from engine import main

if __name__ == '__main__':
    sys.argv.insert(1, 'drift')
    main()
