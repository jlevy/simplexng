"""
SimpleXNG: A simple way to run SearXNG locally
"""

import sys
from pathlib import Path

# Inject the searxng vendor directory into the path before other imports.
_vendor_path = str(Path(__file__).parent / "_vendor")
if _vendor_path not in sys.path:
    sys.path.insert(0, _vendor_path)

# Now we can import the rest normally
import argparse
import logging
import signal
import webbrowser
from importlib.metadata import version
from threading import Timer
from typing import Any

import waitress
from clideps.utils.readable_argparse import ReadableColorFormatter

from simplexng.settings import APP_NAME, get_settings_path, init_settings


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


def get_full_app_version() -> str:
    try:
        simplexng_version = "v" + version(APP_NAME)
    except Exception:
        simplexng_version = "(unknown version)"

    return f"{APP_NAME} {simplexng_version} (SearXNG {get_searxng_version()})"


def get_searxng_version() -> str:
    # Careful, can't import anything until searxng is initialized or it will abort
    if get_settings_path():
        try:
            from searx.version import VERSION_STRING  # pyright: ignore

            return VERSION_STRING  # pyright: ignore
        except ImportError:
            pass
    # Fall back to reading from file if version module is not (yet) available
    try:
        return (Path(__file__).parent / "searxng_version.txt").read_text().strip()[:7]
    except FileNotFoundError:
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
        formatter_class=ReadableColorFormatter, description=__doc__, epilog=get_full_app_version()
    )

    parser.add_argument("--version", action="version", version=get_full_app_version())
    parser.add_argument(
        "-p", "--port", type=int, default=8888, help="Port to run on (default: 8888)"
    )
    parser.add_argument(
        "-H", "--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)"
    )
    parser.add_argument("--open", action="store_true", help="Open browser automatically")
    parser.add_argument(
        "--flask", action="store_true", help="Use flask server instead of waitress (for debugging)"
    )
    parser.add_argument("--settings", help="Path to custom settings.yml file")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")

    return parser


def start_server(args: argparse.Namespace, log: logging.Logger) -> None:
    """
    Start the appropriate server.
    """
    url = f"http://{args.host}:{args.port}"
    server_name = "Flask" if args.flask else "Waitress"

    log.info(f"Starting SimpleXNG with {server_name} server...")
    log.info(f"URL: {url}")
    log.info("Press Ctrl+C to stop")

    if args.open:
        Timer(2, lambda: webbrowser.open(url)).start()
        log.info("Opening browser...")

    if args.flask:
        from searx.webapp import app  # pyright: ignore

        app.run(host=args.host, port=args.port, debug=True)  # pyright: ignore[reportUnknownMemberType]
    else:
        from searx.webapp import application  # pyright: ignore

        waitress.serve(
            application,  # pyright: ignore[reportUnknownArgumentType]
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
    level = logging.DEBUG if args.verbose else logging.INFO
    log = log_setup(level)
    signal.signal(signal.SIGINT, signal_handler)

    try:
        init_settings(args.port, args.host, Path(args.settings) if args.settings else None)
        log.warning("Initialized: %s", get_full_app_version())

        start_server(args, log)
    except Exception as e:
        log.error(f"Error: {e.__class__.__name__}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
