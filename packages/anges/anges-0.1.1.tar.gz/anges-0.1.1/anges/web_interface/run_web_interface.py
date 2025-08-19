#!/usr/bin/env python3

import sys
import logging
from anges.web_interface.web_interface import main

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Failed to start web interface: {e}")
        sys.exit(1)
        logging.error(f"Failed to start web interface: {e}")
        sys.exit(1)