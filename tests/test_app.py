import os
import sqlite3
from unittest import mock

import app as app_module
import db_setup
from conftest import ASSETS, PASSWORD, SANDBOX, USERNAME, upload


def uploads():
    return db_setup.get_uploads()


def test_requires_login(anon_client):
    resp = anon_client.get("/uploads")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_upload_filename_cannot_escape_assets(client):
    resp = upload(client, "../server/evil.py", b"print('pwned')")
    assert resp.status_code == 302
    assert not os.path.exists(os.path.join(SANDBOX, "server", "evil.py"))
    [(_, _, _, stored)] = uploads()
    assert "/" not in stored and ".." not in stored
    assert os.path.isfile(os.path.join(ASSETS, stored))


def test_duplicate_upload_names_do_not_clobber(client):
    upload(client, "a.txt", b"first")
    upload(client, "a.txt", b"second")
    names = [row[3] for row in uploads()]
    assert len(set(names)) == 2
    contents = sorted(open(os.path.join(ASSETS, n), "rb").read() for n in names)
    assert contents == [b"first", b"second"]


def test_rename_cannot_escape_assets(client):
    upload(client, "a.txt")
    [(upload_id, *_)] = uploads()
    resp = client.post(f"/rename/{upload_id}", json={"new_name": "../server/moved.py"})
    assert not os.path.exists(os.path.join(SANDBOX, "server", "moved.py"))
    if resp.status_code == 200:
        new_name = uploads()[0][3]
        assert os.path.isfile(os.path.join(ASSETS, new_name))
    else:
        assert resp.status_code == 400
        assert os.path.isfile(os.path.join(ASSETS, "a.txt"))


def test_rename_cannot_pull_files_into_assets(client):
    victim = os.path.join(SANDBOX, "server", "victim.txt")
    with open(victim, "w") as f:
        f.write("server data")
    client.post("/upload/link", data={"link": "../server/victim.txt"})
    [(link_id, *_)] = uploads()
    resp = client.post(f"/rename/{link_id}", json={"new_name": "stolen.txt"})
    assert resp.status_code == 400
    assert os.path.isfile(victim)
    assert not os.path.exists(os.path.join(ASSETS, "stolen.txt"))


def test_rename_valid_name(client):
    upload(client, "a.txt")
    [(upload_id, *_)] = uploads()
    resp = client.post(f"/rename/{upload_id}", json={"new_name": "b.txt"})
    assert resp.status_code == 200
    assert uploads()[0][3] == "b.txt"
    assert os.path.isfile(os.path.join(ASSETS, "b.txt"))


def test_download_all_misc(client):
    upload(client, "notes.txt", b"hello")
    upload(client, "pic.png", b"png")
    resp = client.get("/download_all_misc")
    assert resp.status_code == 200
    assert resp.headers["Content-Type"] == "application/zip"
    # Only the misc file is consumed; the photo stays.
    assert [row[3] for row in uploads()] == ["pic.png"]


def test_download_all_links_with_single_link(client):
    client.post("/upload/link", data={"link": "https://example.com"})
    resp = client.get("/download_all_links")
    assert resp.status_code == 200
    assert b"https://example.com" in resp.data
    assert uploads() == []


def test_non_http_links_are_not_clickable(client):
    client.post("/upload/link", data={"link": "javascript:alert(document.cookie)"})
    client.post("/upload/link", data={"link": "https://example.com/ok"})
    page = client.get("/uploads").get_data(as_text=True)
    assert 'href="javascript:' not in page
    assert "javascript:alert(document.cookie)" in page
    assert 'href="https://example.com/ok"' in page


def test_session_cookie_is_samesite_strict(anon_client):
    resp = anon_client.post("/login", data={"username": USERNAME, "password": PASSWORD})
    cookie = resp.headers["Set-Cookie"]
    assert "SameSite=Strict" in cookie


def test_main_does_not_enable_debugger_by_default(monkeypatch):
    monkeypatch.delenv("FLASK_DEBUG", raising=False)
    with mock.patch.object(app_module.app, "run") as run:
        app_module.main()
    assert run.call_args.kwargs["debug"] is False


def test_main_debug_opt_in(monkeypatch):
    monkeypatch.setenv("FLASK_DEBUG", "1")
    with mock.patch.object(app_module.app, "run") as run:
        app_module.main()
    assert run.call_args.kwargs["debug"] is True


def test_password_stored_with_slow_hash(fresh_state):
    stored, _, _ = db_setup.get_user(USERNAME)
    assert stored.startswith(("scrypt:", "pbkdf2:"))


def test_legacy_sha256_password_still_works_and_is_upgraded(anon_client):
    salt = os.urandom(16)
    import hashlib

    legacy = hashlib.sha256(salt + b"old-pass").hexdigest()
    with sqlite3.connect(db_setup.DATABASE) as conn:
        conn.execute(
            "INSERT INTO users (username, password, salt) VALUES (?, ?, ?)",
            ("legacy", legacy, salt),
        )
    resp = anon_client.post("/login", data={"username": "legacy", "password": "old-pass"})
    assert resp.status_code == 302 and resp.headers["Location"].endswith("/")
    stored, _, _ = db_setup.get_user("legacy")
    assert stored.startswith(("scrypt:", "pbkdf2:"))


def test_lockout_after_three_failures(anon_client):
    for _ in range(3):
        anon_client.post("/login", data={"username": USERNAME, "password": "wrong"})
    resp = anon_client.post("/login", data={"username": USERNAME, "password": PASSWORD})
    assert resp.status_code == 302
    assert "/lockout" in resp.headers["Location"]
