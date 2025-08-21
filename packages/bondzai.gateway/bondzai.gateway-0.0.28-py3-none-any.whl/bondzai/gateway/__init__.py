import os
import argparse
import signal
from pathlib import Path

from .core.application import Application, CONFIG_DEFAULT_PATH


CMD_NAME = "bondzai.gateway"
__version__ = "0.0.28"


def run():
    parser = argparse.ArgumentParser(
        prog=CMD_NAME,
        description="Davinsy Gateway"
    )

    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument(
        "-c", "--config",
        dest="config", help="Path to the YAML file for config.", 
        type=Path, default=CONFIG_DEFAULT_PATH
    )

    args = parser.parse_args()

    # TMP Fix for Windows CTRL + C not stopping threads
    if os.name == "nt":
        signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = Application(Path(args.config))
    app.run()
