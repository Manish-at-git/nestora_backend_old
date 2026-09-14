"""
Iteration 3 tests — Announcements + Events feature.
Covers:
- Public GET /announcements + /events require any authenticated user (member OK).
- POST/PUT/DELETE under /admin/* require admin auth (401 without token, 403 for member).
- Seeded announcements + events exist on first run.
- Full admin CRUD roundtrip for announcements (create -> list -> update -> delete).
- Full admin CRUD roundtrip for events (create -> scope filter -> update -> delete).
- Category validation and end<start validation.
"""
import os
import uuid
from datetime import datetime, timedelta, timezone

import pytest
import requests

BASE_URL = os.environ.get(
    "REACT_APP_BACKEND_URL",
    "https://nestora-code-auth.preview.emergentagent.com",
).rstrip("/")
API = f"{BASE_URL}/api"

ADMIN_EMAIL = "admin@nestora.io"
ADMIN_PASSWORD = "Admin@Nestora2026"


# ---------- Fixtures ----------
@pytest.fixture(scope="module")
def s():
    sess = requests.Session()
    sess.headers.update({"Content-Type": "application/json"})
    return sess


@pytest.fixture(scope="module")
def admin_headers(s):
    r = s.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert r.status_code == 200, f"admin login failed: {r.status_code} {r.text}"
    tok = r.json()["token"]
    return {"Authorization": f"Bearer {tok}", "Content-Type": "application/json"}


@pytest.fixture(scope="module")
def member_headers(s):
    """Login as member using NST-DEMO3 (create if needed)."""
    email = "rohan.demo@nestora.io"
    pw = "Nestora@2026"
    r = s.post(f"{API}/auth/login", json={"email": email, "password": pw})
    if r.status_code != 200:
        # create the account first via NST-DEMO3
        r2 = s.post(f"{API}/create-account", json={
            "code": "NST-DEMO3", "email": email,
            "password": pw, "confirm_password": pw,
        })
        if r2.status_code not in (200, 409):
            pytest.skip(f"cannot create member: {r2.status_code} {r2.text}")
        if r2.status_code == 409:
            # account already exists but login failed -> can't proceed
            pytest.skip("member exists but password unknown")
        tok = r2.json()["token"]
    else:
        tok = r.json()["token"]
    return {"Authorization": f"Bearer {tok}", "Content-Type": "application/json"}


# ---------- Auth guards ----------
def test_announcements_get_requires_auth(s):
    r = requests.get(f"{API}/announcements")
    assert r.status_code == 401


def test_events_get_requires_auth(s):
    r = requests.get(f"{API}/events")
    assert r.status_code == 401


def test_admin_announcements_post_no_token(s):
    r = requests.post(f"{API}/admin/announcements", json={
        "title": "should fail", "body": "no auth", "category": "general"
    })
    assert r.status_code == 401


def test_admin_events_post_no_token(s):
    r = requests.post(f"{API}/admin/events", json={
        "title": "should fail", "starts_at": datetime.now(timezone.utc).isoformat()
    })
    assert r.status_code == 401


def test_admin_announcements_post_member_forbidden(s, member_headers):
    r = s.post(f"{API}/admin/announcements",
               headers=member_headers,
               json={"title": "x", "body": "xx", "category": "general"})
    assert r.status_code == 403


def test_admin_events_post_member_forbidden(s, member_headers):
    r = s.post(f"{API}/admin/events",
               headers=member_headers,
               json={"title": "x", "starts_at": datetime.now(timezone.utc).isoformat()})
    assert r.status_code == 403


# ---------- Seeded content ----------
def test_seeded_announcements_present(s, member_headers):
    r = s.get(f"{API}/announcements", headers=member_headers)
    assert r.status_code == 200
    rows = r.json()
    assert isinstance(rows, list)
    titles = " | ".join(a["title"] for a in rows)
    assert "Community garden refresh" in titles or len(rows) >= 2, \
        f"expected seeded announcements; got: {titles}"
    # Pinned ordering — pinned rows must appear before non-pinned
    seen_unpinned = False
    for a in rows:
        if not a["pinned"]:
            seen_unpinned = True
        elif seen_unpinned:
            pytest.fail("pinned announcement appeared after an unpinned one")
    # Every row has required keys and category is valid
    for a in rows:
        for k in ("id", "title", "body", "category", "pinned", "created_at"):
            assert k in a, f"missing key {k} in announcement"
        assert a["category"] in ("general", "maintenance", "urgent", "celebration")
        assert isinstance(a["pinned"], bool)


def test_seeded_events_present(s, member_headers):
    r = s.get(f"{API}/events?scope=upcoming", headers=member_headers)
    assert r.status_code == 200
    rows = r.json()
    assert isinstance(rows, list)
    assert len(rows) >= 1, "expected at least 1 upcoming seeded event"
    for ev in rows:
        for k in ("id", "title", "starts_at"):
            assert k in ev


def test_events_scope_all_gte_upcoming(s, member_headers):
    r1 = s.get(f"{API}/events?scope=upcoming", headers=member_headers)
    r2 = s.get(f"{API}/events?scope=all", headers=member_headers)
    assert r1.status_code == 200 and r2.status_code == 200
    assert len(r2.json()) >= len(r1.json())


# ---------- Announcement CRUD ----------
class TestAnnouncementCRUD:
    tag = f"TEST-{uuid.uuid4().hex[:6]}"

    def test_a_create(self, s, admin_headers):
        payload = {
            "title": f"{self.tag} urgent notice",
            "body": "This is a test urgent announcement body.",
            "category": "urgent",
            "pinned": True,
        }
        r = s.post(f"{API}/admin/announcements", headers=admin_headers, json=payload)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["ok"] is True
        assert isinstance(data["id"], int)
        pytest.new_ann_id = data["id"]

        # verify persisted via GET
        r2 = s.get(f"{API}/announcements", headers=admin_headers)
        assert r2.status_code == 200
        rows = r2.json()
        row = next((x for x in rows if x["id"] == data["id"]), None)
        assert row is not None, "created announcement not found in list"
        assert row["title"] == payload["title"]
        assert row["category"] == "urgent"
        assert row["pinned"] is True

    def test_b_invalid_category(self, s, admin_headers):
        r = s.post(f"{API}/admin/announcements", headers=admin_headers, json={
            "title": f"{self.tag} bad", "body": "body", "category": "spam"
        })
        assert r.status_code == 422 or r.status_code == 400

    def test_c_update(self, s, admin_headers):
        aid = getattr(pytest, "new_ann_id", None)
        assert aid is not None
        r = s.put(f"{API}/admin/announcements/{aid}", headers=admin_headers, json={
            "title": f"{self.tag} edited title",
            "body": "Edited body text.",
            "category": "general",
            "pinned": False,
        })
        assert r.status_code == 200, r.text
        # verify persisted
        r2 = s.get(f"{API}/announcements", headers=admin_headers)
        row = next((x for x in r2.json() if x["id"] == aid), None)
        assert row is not None
        assert row["title"] == f"{self.tag} edited title"
        assert row["category"] == "general"
        assert row["pinned"] is False

    def test_d_update_not_found(self, s, admin_headers):
        r = s.put(f"{API}/admin/announcements/999999", headers=admin_headers, json={
            "title": "Nonexistent title",
            "body": "Nonexistent body content",
            "category": "general",
            "pinned": False,
        })
        assert r.status_code == 404

    def test_e_delete(self, s, admin_headers):
        aid = getattr(pytest, "new_ann_id", None)
        assert aid is not None
        r = s.delete(f"{API}/admin/announcements/{aid}", headers=admin_headers)
        assert r.status_code == 200
        r2 = s.get(f"{API}/announcements", headers=admin_headers)
        assert not any(x["id"] == aid for x in r2.json())

    def test_f_delete_not_found(self, s, admin_headers):
        r = s.delete(f"{API}/admin/announcements/999999", headers=admin_headers)
        assert r.status_code == 404


# ---------- Event CRUD ----------
class TestEventCRUD:
    tag = f"TEST-EV-{uuid.uuid4().hex[:6]}"

    def test_a_create_upcoming(self, s, admin_headers):
        starts = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()
        ends = (datetime.now(timezone.utc) + timedelta(days=5, hours=2)).isoformat()
        payload = {
            "title": f"{self.tag} Test event",
            "description": "Test description.",
            "location": "TEST hall",
            "starts_at": starts,
            "ends_at": ends,
        }
        r = s.post(f"{API}/admin/events", headers=admin_headers, json=payload)
        assert r.status_code == 200, r.text
        data = r.json()
        pytest.new_event_id = data["id"]

        # Appears in upcoming
        r2 = s.get(f"{API}/events?scope=upcoming", headers=admin_headers)
        assert any(x["id"] == data["id"] for x in r2.json())

    def test_b_reject_end_before_start(self, s, admin_headers):
        starts = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()
        ends = (datetime.now(timezone.utc) + timedelta(days=4)).isoformat()  # end < start
        r = s.post(f"{API}/admin/events", headers=admin_headers, json={
            "title": f"{self.tag} bad", "starts_at": starts, "ends_at": ends
        })
        assert r.status_code == 400

    def test_c_scope_past_excludes_future(self, s, admin_headers):
        r = s.get(f"{API}/events?scope=past", headers=admin_headers)
        assert r.status_code == 200
        # our just-created future event must NOT be in past
        eid = getattr(pytest, "new_event_id", None)
        assert not any(x["id"] == eid for x in r.json())

    def test_d_update(self, s, admin_headers):
        eid = getattr(pytest, "new_event_id", None)
        assert eid is not None
        new_start = (datetime.now(timezone.utc) + timedelta(days=10)).isoformat()
        r = s.put(f"{API}/admin/events/{eid}", headers=admin_headers, json={
            "title": f"{self.tag} updated",
            "description": "updated desc",
            "location": "New TEST hall",
            "starts_at": new_start,
            "ends_at": None,
        })
        assert r.status_code == 200, r.text
        r2 = s.get(f"{API}/events?scope=all", headers=admin_headers)
        row = next((x for x in r2.json() if x["id"] == eid), None)
        assert row is not None
        assert row["title"] == f"{self.tag} updated"
        assert row["location"] == "New TEST hall"

    def test_e_update_not_found(self, s, admin_headers):
        r = s.put(f"{API}/admin/events/999999", headers=admin_headers, json={
            "title": "Nonexistent event",
            "starts_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        })
        assert r.status_code == 404

    def test_f_delete(self, s, admin_headers):
        eid = getattr(pytest, "new_event_id", None)
        assert eid is not None
        r = s.delete(f"{API}/admin/events/{eid}", headers=admin_headers)
        assert r.status_code == 200
        r2 = s.get(f"{API}/events?scope=all", headers=admin_headers)
        assert not any(x["id"] == eid for x in r2.json())

    def test_g_delete_not_found(self, s, admin_headers):
        r = s.delete(f"{API}/admin/events/999999", headers=admin_headers)
        assert r.status_code == 404
