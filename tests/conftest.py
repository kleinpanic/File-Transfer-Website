import io
import os
import shutil
import sys
import tempfile

import pytest
from flask.testing import FlaskClient

# The server modules use paths relative to the working directory
# (transfer_service.db, locked_ips.txt, ../assets) and app.py creates
# ~/Downloads at import time, so run everything inside a scratch tree.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SANDBOX = tempfile.mkdtemp(prefix="ftw-tests-")
os.makedirs(os.path.join(SANDBOX, "server"))
os.chdir(os.path.join(SANDBOX, "server"))
os.environ["HOME"] = SANDBOX
sys.path.insert(0, os.path.join(REPO_ROOT, "server"))

import app as app_module  # noqa: E402
import db_setup  # noqa: E402
import security  # noqa: E402

ASSETS = os.path.join(SANDBOX, "assets")
USERNAME = "tester"
PASSWORD = "correct horse"


class HTTPSClient(FlaskClient):
    """Talisman redirects plain-HTTP requests to HTTPS, so default to it."""

    def open(self, *args, **kwargs):
        kwargs.setdefault("base_url", "https://localhost")
        return super().open(*args, **kwargs)


@pytest.fixture
def fresh_state():
    if os.path.exists(db_setup.DATABASE):
        os.remove(db_setup.DATABASE)
    db_setup.initialize_db()
    open(security.LOCKOUT_FILE, "w").close()
    security.FAILED_ATTEMPTS.clear()
    shutil.rmtree(ASSETS, ignore_errors=True)
    os.makedirs(ASSETS)
    db_setup.add_user(USERNAME, PASSWORD)
    yield


@pytest.fixture
def anon_client(fresh_state):
    app_module.app.config["TESTING"] = True
    app_module.app.test_client_class = HTTPSClient
    return app_module.app.test_client()


@pytest.fixture
def client(anon_client):
    resp = anon_client.post("/login", data={"username": USERNAME, "password": PASSWORD})
    assert resp.status_code == 302 and resp.headers["Location"].endswith("/")
    return anon_client


def upload(client, name, data=b"data"):
    return client.post(
        "/upload/files",
        data={"files[]": (io.BytesIO(data), name)},
        content_type="multipart/form-data",
    )
