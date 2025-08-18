"""CLI Testing tool for checking local functionality"""

import argparse
import json
import os
import re
import sys

from dataclasses import dataclass

from ptpython import embed

from jbutils.utils.config import Configurator
from jbutils import jbutils

TOOL_DIR = os.path.dirname(__file__)
JBUTILS_DIR = os.path.dirname(TOOL_DIR)
PROJ_DIR = os.path.dirname(JBUTILS_DIR)
UTILS_PATH = os.path.join(JBUTILS_DIR, "utils", "utils.py")

_parser = argparse.ArgumentParser(description=__doc__)
cmn_handler = jbutils.add_common_args(_parser, UTILS_PATH, proj_dir=PROJ_DIR)
args = _parser.parse_args()


def main() -> None:
    cfg = Configurator(app_name="cfgtest")
    dpath = "saved_data.test3.yaml"
    cmn_handler()
    sys.exit(
        embed(
            globals=globals(),
            locals=locals(),
            history_filename="jbutils_cli.history",
        )
    )


if __name__ == "__main__":
    main()
