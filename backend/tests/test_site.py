import pytest


@pytest.fixture(autouse=True)
def react_build(settings, tmp_path):
    """A stand-in for frontend/dist so these tests don't need `npm run build`."""
    (tmp_path / "index.html").write_text("<div id='root'></div>")
    settings.TEMPLATES[0]["DIRS"] = [tmp_path]


@pytest.mark.parametrize("path", ["/", "/?ref=MIKA123", "/any/deep/link"])
def test_react_app_served(client, path):
    res = client.get(path)
    assert res.status_code == 200 and b"root" in res.content


def test_favicon_redirect(client):
    assert client.get("/favicon.ico")["Location"] == "/static/favicon.png"


def test_unknown_api_path_is_404_not_react(client):
    assert client.get("/api/nope/").status_code == 404
