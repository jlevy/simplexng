import logging
import os
import secrets
import sys
from functools import cache
from pathlib import Path

import yaml
from platformdirs import PlatformDirs
from platformdirs.unix import Unix
from strif import AtomicVar

log = logging.getLogger()

APP_NAME = "SimpleXNG"

CFG_NAME = APP_NAME.lower()

SETTINGS_NAME = f"{CFG_NAME}_settings.yml"


_settings_path: AtomicVar[Path | None] = AtomicVar(None)


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


def get_settings_path() -> Path | None:
    return _settings_path.copy()


def init_settings(
    port: int | None = None,
    host: str | None = None,
    settings_path: Path | None = None,
) -> None:
    """
    One-time initialization of settings.
    """
    with _settings_path.lock:
        if _settings_path.value:
            raise RuntimeError("Settings already initialized")

        if settings_path:
            if not settings_path.exists():
                raise FileNotFoundError(f"Settings file not found: {settings_path}")
            log.warning("Using specified settings file: %s", settings_path)
            _settings_path.set(settings_path)
            return
        else:
            # Create from template and host/port
            path = get_settings_dir(CFG_NAME) / SETTINGS_NAME

            if not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)

                template_path = get_bundled_template()
                settings = yaml.safe_load(template_path.read_text())

                settings["server"]["port"] = port
                settings["server"]["bind_address"] = host
                # Generate a cryptographically secure random secret key
                settings["server"]["secret_key"] = secrets.token_hex(16)

                content = (
                    f"# Generated from template {template_path.name}\n"
                    f"# Port: {port}, Host: {host}\n"
                    f"# Random secret key generated automatically\n\n"
                    f"{yaml.dump(settings, default_flow_style=False)}"
                )
                path.write_text(content)

                log.warning("Wrote new settings file (including random secret key): %s", path)
            else:
                log.warning("Using existing settings file: %s", path)

        _settings_path.set(path)

        # Set configs for SearXNG to use this path (and its parent as the config path)
        os.environ["SEARXNG_SETTINGS_PATH"] = str(path)
