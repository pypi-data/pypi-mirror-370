import os
import sys
from pathlib import Path

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.append(parent_dir)

import ingenious.cli as cli
from ingenious.config.config import get_config

os.environ["INGENIOUS_WORKING_DIR"] = str(Path(os.getcwd()))
# Make sure you have set the environment variables
_config = get_config()


def run_cli():
    cli.run_all(
        profile_dir=None,  # This is set by your environment variables
        project_dir=None,  # This is set by your environment variables
        host=_config.web_configuration.ip_address,
        port=_config.web_configuration.port,
    )


run_cli()
