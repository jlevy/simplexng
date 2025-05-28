# SimpleXNG

SimpleXNG is a simplified package of [SearXNG](https://github.com/searxng/searxng) to
make it a single command to run for local use.

The [official install options](https://docs.searxng.org/admin/installation.html) for
SearXNG seem quite complex, which may be necessary if you are setting up a server others
use, but not not necessary if all you want to do is run it locally.

This is a tiny package to streamline running it locally, without Docker, on macOS,
Linux, or Windows.

It [uv](https://github.com/astral-sh/uv) to manage the Python dependencies, omits
Apache, Nginx, and Docker setup, and uses the minimal template that does not enable
features like rate limiting or Redis.
(You can adjust these later if desired.)

## Running

We suggest [installing uv](https://docs.astral.sh/uv/getting-started/installation/) if
you haven't already.
Then install SimpleXNG:

```shell
uv tool install simplexng
```

To run:

```shell
simplexng --open
```

More options:

```shell
simplexng --help
```

As shown in the logs, it sets up a minimal config file (on macOS and Linux it will be
`~/.config/simplexng/settings.yml`), which you can edit if desired.

* * *

## Project Docs

For how to install uv and Python, see [installation.md](installation.md).

For development workflows, see [development.md](development.md).

For instructions on publishing to PyPI, see [publishing.md](publishing.md).

* * *

*This project was built from
[simple-modern-uv](https://github.com/jlevy/simple-modern-uv).*
