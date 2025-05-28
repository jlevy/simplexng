import logging
import sys
from functools import cache
from pathlib import Path

import yaml
from platformdirs import PlatformDirs
from platformdirs.unix import Unix

log = logging.getLogger()

APP_NAME = "SimpleXNG"

CFG_NAME = APP_NAME.lower()

SETTINGS_NAME = f"{CFG_NAME}_settings.yml"


@cache
def get_settings_dir(name: str) -> Path:
    """
    Get the directory for settings.
    Use ~/.config on macOS and Linux and platformdirs default on Windows.
    """
    if sys.platform == "darwin":
        dirs = Unix(name, appauthor=False, ensure_exists=True)
    else:
        dirs = PlatformDirs(name, appauthor=False, ensure_exists=True)

    return Path(dirs.user_config_dir)


def get_bundled_template() -> Path:
    return Path(__file__).parent / "settings" / "settings_template.yml"


@cache
def get_or_init_settings(
    port: int = 8888,
    host: str = "127.0.0.1",
    template_path: Path | None = None,
) -> Path:
    """
    Get current settings or create default settings from basic template.
    """
    settings_path = get_settings_dir(CFG_NAME) / SETTINGS_NAME

    if settings_path.exists():
        log.warning("Using existing settings: %s", settings_path)
        return settings_path

    else:
        # Create from template.
        settings_path.parent.mkdir(parents=True, exist_ok=True)

        if template_path is None:
            template_path = get_bundled_template()

        settings = yaml.safe_load(template_path.read_text())

        settings["server"]["port"] = port
        settings["server"]["bind_address"] = host

        content = (
            f"# Generated from template {template_path.name}\n"
            f"# Port: {port}, Host: {host}\n\n"
            f"{yaml.dump(settings, default_flow_style=False)}"
        )
        settings_path.write_text(content)

        log.warning("Wrote new settings file: %s", settings_path)

        return settings_path
