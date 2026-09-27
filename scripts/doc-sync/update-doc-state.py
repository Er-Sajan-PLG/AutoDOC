#!/usr/bin/env python3
"""AutoDOC state entry point; see engine.py."""
import sys
from engine import main

if __name__ == '__main__':
    sys.argv.insert(1, 'state')
    main()
