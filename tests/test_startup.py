from simplexng.simplexng import get_full_app_version


def test_startup():
    version: str = get_full_app_version()
    assert version and "unknown" not in version
