import sys
from pathlib import Path

import toml

from ._consts import APP_NAME, ERROR, Colors, cprint

CONFIG_FILES = ["ties.toml", "pyproject.toml"]


def load_config() -> dict:
    """Load configuration from 'ties.toml' or 'pyproject.toml'."""
    current_dir = Path.cwd()
    for directory in [current_dir, *list(current_dir.parents)]:
        for config_file_name in CONFIG_FILES:
            config_path = directory / config_file_name
            if config_path.is_file():
                try:
                    with open(config_path) as f:
                        config_data = toml.load(f)

                    if config_file_name == "pyproject.toml":
                        ties_config = config_data.get("tool", {}).get(APP_NAME, {})
                    else:
                        ties_config = config_data

                    if ties_config:
                        return ties_config

                except Exception as e:
                    cprint(
                        f"❌ Error parsing {config_path}: {e}", Colors.RED, bold=True
                    )
                    sys.exit(ERROR)
    return {}
