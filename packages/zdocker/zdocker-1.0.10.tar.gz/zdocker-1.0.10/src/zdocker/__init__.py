#!/usr/bin/env python3

from zdocker.build import BuildCommand
from zdocker.cct import Cct


def cct_main():
    """
    Main entry point for the CCT (Conan Command Tool) functionality.
    """
    cct = Cct()
    cct.execute()


def zdocker_main():
    BuildCommand().run()
