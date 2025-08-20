def test_imports():
    import docmaplabs_marketing_package as pkg  # noqa: F401
    from docmaplabs_marketing_package.cli import run  # noqa: F401
    from docmaplabs_marketing_package.server import app  # noqa: F401


def test_normalize_query():
    from docmaplabs_marketing_package.twitter_client import normalize_query
    q = normalize_query(["NHS waiting times", "from:NHSEngland", "gp"])
    assert '"NHS waiting times"' in q and "from:NHSEngland" in q and "gp" in q


