# searxng-local

SimpleXNG is a simplified package of [SearXNG](https://github.com/searxng/searxng) to
make it a single command to run for local use.

The [official install options](https://docs.searxng.org/admin/installation.html) all
seemed quite complex if all you want to do is run it locally.

This is a tiny package to streamline running it locally, without Docker, on macOS,
Linux, or Windows. It omits the dependencies like Apache, Nginx, and Docker and uses
[uv](https://github.com/astral-sh/uv) to manage the Python dependencies.
It disables features like rate limiting and Redis and runs with all default options.
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
simplexng 
```

More options:

```shell
simplexng --help
```

* * *

## Project Docs

For how to install uv and Python, see [installation.md](installation.md).

For development workflows, see [development.md](development.md).

For instructions on publishing to PyPI, see [publishing.md](publishing.md).

* * *

*This project was built from
[simple-modern-uv](https://github.com/jlevy/simple-modern-uv).*
