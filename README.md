# SimpleXNG

SimpleXNG is a simplified package of [SearXNG](https://github.com/searxng/searxng) to
make it a single command to run for local use.

## Why?

The [official install options](https://docs.searxng.org/admin/installation.html) for
SearXNG are a bit complex and assume admin privileges to set up.
This can be simplified a lot if you’re just wanting to run it locally for your own use.

SimpleXNG is a tiny package to run SearXNG locally on macOS, Linux, or Windows.

I wrote this since a friend was asking me why it wasn’t easier to set up for “localhost”
use or embedded use.
I thought I’d see if it worked as a minimal, modern uv package.

## Running

1. [Install uv](https://docs.astral.sh/uv/getting-started/installation/) if you haven’t
   already.

2. Install and run:

   ```shell
   uv tool install --upgrade simplexng
   simplexng --open
   ```

   Or if you’re in a hurry, in one line:

   ```shell
   uvx --upgrade simplexng --open
   ```

   This will install the latest version of SimpleXNG and open it in your browser.

See more options:

```shell
simplexng --help
```

## Notes

- SimpleXNG uses [uv](https://github.com/astral-sh/uv) to manage the Python
  dependencies.

- It omits Apache, Nginx, and Docker setup.

- It by default uses the
  [minimal template settings](https://github.com/searxng/searxng/blob/master/utils/templates/etc/searxng/settings.yml)
  with Redis and rate limiting turned off.
  (You can adjust the settings file if desired.)

- Since SearXNG is distributed in Docker images only, we vendor a recent copy of SearXNG
  so it is all available in a single package from PyPI for quick installation.

- On first run, it sets up a minimal config file (on macOS and Linux it will be
  `~/.config/simplexng/settings.yml`), which you can edit and will be used on subsequent
  runs.

- You can see the version of SearXNG being used with `simplexng --version`. If you want
  a newer or different build, you can clone this repo and run:
  ```shell
  ./scripts/clone_searxng.sh HEAD   # Or pick a revision
  uv run simplexng
  ```

## Thoughts?

If this is useful or of interest or have feedback, file an issue or drop a comment [on
my post about SimpleXNG](https://github.com/searxng/searxng/discussions/5082).

## License

This code and SearXNG are AGPL-3.0 licensed.

* * *

## Project Docs

For how to install uv and Python, see [installation.md](installation.md).

For development workflows, see [development.md](development.md).

For instructions on publishing to PyPI, see [publishing.md](publishing.md).

* * *

*This project was built from
[simple-modern-uv](https://github.com/jlevy/simple-modern-uv).*
