# Copyright 2024 Science project contributors.
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

import os
import subprocess
import sys
from typing import NoReturn

from . import InputError, ScienceNotFound, ensure_installed
from ._internal.colors import color_support
from ._internal.platform import CURRENT_PLATFORM


def main() -> NoReturn:
    try:
        science_exe = ensure_installed()
    except InputError as e:
        with color_support() as colors:
            sys.exit(f"{colors.red('Configuration error')}: {colors.yellow(str(e))}")
    except ScienceNotFound as e:
        with color_support() as colors:
            sys.exit(colors.red(str(e)))

    argv = [str(science_exe.path), *sys.argv[1:]]
    try:
        if CURRENT_PLATFORM.is_windows:
            sys.exit(subprocess.run(argv).returncode)
        else:
            os.execv(science_exe.path, argv)
    except OSError as e:
        with color_support() as colors:
            sys.exit(colors.red(str(e)))
