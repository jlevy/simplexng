#!/usr/bin/env python3
"""
SimpleXNG: A simple way to run SearXNG locally
"""

import argparse
import logging
import os
import signal
import sys
import webbrowser
from importlib.metadata import version
from pathlib import Path
from threading import Timer
from typing import Any

from clideps.utils.readable_argparse import ReadableColorFormatter
from waitress import serve

from simplexng.settings import APP_NAME, get_or_init_settings


def log_setup(level: int) -> logging.Logger:
    """
    Setup logging with rich console formatting when available.
    """
    is_console = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
    if is_console:
        try:
            from rich.console import Console
            from rich.logging import RichHandler

            console = Console()
            handler = RichHandler(
                console=console,
                show_time=False,
                show_path=False,
                markup=True,
                rich_tracebacks=True,
            )
            handler.setFormatter(logging.Formatter(fmt="%(message)s"))

            logging.basicConfig(level=level, handlers=[handler], force=True)
        except ImportError:
            # Fallback to basic formatting if rich is not available
            logging.basicConfig(
                level=level, format="%(levelname)s: %(message)s", stream=sys.stdout, force=True
            )
    else:
        # Use basic formatting for non-console environments
        logging.basicConfig(
            level=level, format="%(levelname)s: %(message)s", stream=sys.stdout, force=True
        )

    return logging.getLogger(APP_NAME)


def get_app_version() -> str:
    try:
        return "v" + version(APP_NAME)
    except Exception:
        return "(unknown version)"


def signal_handler(_signum: int, _frame: Any) -> None:
    """
    Handle Ctrl+C gracefully.
    """
    log = logging.getLogger(APP_NAME)
    log.warning("Shutting down SearXNG...")
    sys.exit(0)


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure argument parser.
    """
    parser = argparse.ArgumentParser(
        formatter_class=ReadableColorFormatter,
        description=__doc__,
        epilog=f"{APP_NAME} {get_app_version()}",
    )

    parser.add_argument(
        "-p", "--port", type=int, default=8888, help="Port to run on (default: 8888)"
    )
    parser.add_argument(
        "-H", "--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)"
    )
    parser.add_argument("--open", action="store_true", help="Open browser automatically")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode (Flask dev server)")
    parser.add_argument("--settings", help="Path to custom settings.yml file")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")

    return parser


def start_server(args: argparse.Namespace, log: logging.Logger) -> None:
    """
    Start the appropriate server.
    """
    url = f"http://{args.host}:{args.port}"
    server_name = "Flask" if args.debug else "Waitress"

    log.info(f"Starting SimpleXNG with {server_name} server...")
    log.info(f"URL: {url}")
    log.info("Press Ctrl+C to stop")

    if args.open:
        Timer(1.5, lambda: webbrowser.open(url)).start()
        log.info("Opening browser...")

    if args.debug:
        from searx.webapp import app

        app.run(host=args.host, port=args.port, debug=True)
    else:
        from searx.webapp import application

        serve(
            application,
            host=args.host,
            port=args.port,
            threads=4,
            connection_limit=100,
            cleanup_interval=30,
        )


def main() -> None:
    """
    Main CLI entry point.
    """
    parser = create_parser()
    args = parser.parse_args()

    # Set up logging and signal handling
    level = logging.DEBUG if args.verbose or args.debug else logging.INFO
    log = log_setup(level)
    signal.signal(signal.SIGINT, signal_handler)

    # Prepare settings
    if args.settings:
        settings_path = Path(args.settings)
        if not settings_path.exists():
            raise FileNotFoundError(f"Settings file not found: {settings_path}")
        log.warning(f"Using custom settings: {args.settings}")
    else:
        settings_path = get_or_init_settings(args.port, args.host)

    # Set configs for SearXNG to use this path (and its parent as the config path)
    os.environ["SEARXNG_SETTINGS_PATH"] = str(settings_path)

    try:
        start_server(args, log)
    except Exception as e:
        log.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
