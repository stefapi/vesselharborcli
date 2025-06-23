#!/usr/bin/env python3
"""VesselHarbor CLI - A command-line tool for interacting with the VesselHarbor API."""

import sys

from vesselharborcli.__main__ import main as cli_main
import threading

_orig_init = threading.Thread.__init__

def debug_thread_init(self, *args, **kwargs):
    import traceback
    traceback.print_stack()
    return _orig_init(self, *args, **kwargs)

threading.Thread.__init__ = debug_thread_init

def main():
    """Run the CLI application."""
    return cli_main()


if __name__ == "__main__":
    ret = main()
    exit(ret)
