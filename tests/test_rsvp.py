"""
Iteration 4 tests — Event RSVP feature.

Covers:
- POST /api/events/{id}/rsvp (going/maybe/not_going) creates + idempotently upserts.
- Invalid RSVP status is rejected with 422.
- DELETE /api/events/{id}/rsvp clears a member's RSVP.
- GET /api/events?scope=upcoming returns enriched fields: rsvp_counts, my_rsvp_status, attendees_preview.
- my_rsvp_status is per-caller (Priya != Aarav).
- Counts include RSVPs from all users.
- attendees_preview capped at 6.
- GET /api/admin/events/{id}/rsvps: admin-only.
- Non-admin (member) gets 403; anonymous gets 401.
- 404 for non-existent event on RSVP + admin endpoints.

NOTE: Backend `get_current_account` reads the `access_token` cookie FIRST, then
falls back to Authorization header. If we shared one requests.Session across
users, cookies from the last login would silently override the Bearer token —
so each user gets its OWN Session.
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
PRIYA_EMAIL = "priya.demo@nestora.io"
AARAV_EMAIL = "aarav.demo@nestora.io"
MEMBER_PASSWORD = "Nestora@2026"


# ---------- Session helpers ----------
def _new_session_for(email, pw):
    sess = requests.Session()
    sess.headers.update({"Content-Type": "application/json"})
    r = sess.post(f"{API}/auth/login", json={"email": email, "password": pw})
    if r.status_code != 200:
        pytest.skip(f"login failed for {email}: {r.status_code} {r.text}")
    tok = r.json()["token"]
    sess.headers["Authorization"] = f"Bearer {tok}"
    return sess


@pytest.fixture(scope="module")
def admin_s():
    return _new_session_for(ADMIN_EMAIL, ADMIN_PASSWORD)


@pytest.fixture(scope="module")
def priya_s():
    return _new_session_for(PRIYA_EMAIL, MEMBER_PASSWORD)


@pytest.fixture(scope="module")
def aarav_s():
    return _new_session_for(AARAV_EMAIL, MEMBER_PASSWORD)


@pytest.fixture(scope="module")
def event_id(admin_s):
    """Create a fresh event for RSVP tests, cleaned up after (cascade removes rsvps)."""
    starts = (datetime.now(timezone.utc) + timedelta(days=14)).isoformat()
    ends = (datetime.now(timezone.utc) + timedelta(days=14, hours=2)).isoformat()
    r = admin_s.post(f"{API}/admin/events", json={
        "title": f"TEST-RSVP-{uuid.uuid4().hex[:6]}",
        "description": "RSVP fixture event",
        "location": "Test hall",
        "starts_at": starts,
        "ends_at": ends,
    })
    assert r.status_code == 200, r.text
    eid = r.json()["id"]
    yield eid
    admin_s.delete(f"{API}/admin/events/{eid}")


def _find(rows, eid):
    return next((e for e in rows if e["id"] == eid), None)


# ---------- RSVP validation + auth ----------
def test_rsvp_requires_auth(event_id):
    r = requests.post(f"{API}/events/{event_id}/rsvp", json={"status": "going"})
    assert r.status_code == 401


def test_rsvp_invalid_status_422(priya_s, event_id):
    r = priya_s.post(f"{API}/events/{event_id}/rsvp", json={"status": "unknown"})
    assert r.status_code == 422, r.text


def test_rsvp_event_not_found_404(priya_s):
    r = priya_s.post(f"{API}/events/999999/rsvp", json={"status": "going"})
    assert r.status_code == 404


# ---------- RSVP set + upsert + delete lifecycle ----------
class TestRsvpLifecycle:
    def test_a_set_going(self, priya_s, event_id):
        r = priya_s.post(f"{API}/events/{event_id}/rsvp", json={"status": "going"})
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["ok"] is True
        assert data["status"] == "going"
        ev = _find(priya_s.get(f"{API}/events?scope=upcoming").json(), event_id)
        assert ev is not None
        assert ev["my_rsvp_status"] == "going"
        assert ev["rsvp_counts"]["going"] >= 1

    def test_b_upsert_maybe(self, priya_s, event_id):
        r = priya_s.post(f"{API}/events/{event_id}/rsvp", json={"status": "maybe"})
        assert r.status_code == 200
        ev = _find(priya_s.get(f"{API}/events?scope=upcoming").json(), event_id)
        assert ev["my_rsvp_status"] == "maybe"
        assert ev["rsvp_counts"]["maybe"] >= 1

    def test_c_upsert_not_going(self, priya_s, event_id):
        r = priya_s.post(f"{API}/events/{event_id}/rsvp", json={"status": "not_going"})
        assert r.status_code == 200
        ev = _find(priya_s.get(f"{API}/events?scope=upcoming").json(), event_id)
        assert ev["my_rsvp_status"] == "not_going"
        assert ev["rsvp_counts"]["not_going"] >= 1

    def test_d_delete_clears(self, priya_s, event_id):
        r = priya_s.delete(f"{API}/events/{event_id}/rsvp")
        assert r.status_code == 200
        ev = _find(priya_s.get(f"{API}/events?scope=upcoming").json(), event_id)
        assert ev["my_rsvp_status"] is None

    def test_e_delete_idempotent(self, priya_s, event_id):
        r = priya_s.delete(f"{API}/events/{event_id}/rsvp")
        assert r.status_code == 200


# ---------- Per-user my_rsvp_status + shared counts ----------
class TestMultiUser:
    def test_a_priya_going_aarav_maybe(self, priya_s, aarav_s, event_id):
        r1 = priya_s.post(f"{API}/events/{event_id}/rsvp", json={"status": "going"})
        r2 = aarav_s.post(f"{API}/events/{event_id}/rsvp", json={"status": "maybe"})
        assert r1.status_code == 200 and r2.status_code == 200

    def test_b_priya_view(self, priya_s, event_id):
        ev = _find(priya_s.get(f"{API}/events?scope=upcoming").json(), event_id)
        assert ev is not None
        assert ev["my_rsvp_status"] == "going"
        assert ev["rsvp_counts"]["going"] >= 1
        assert ev["rsvp_counts"]["maybe"] >= 1

    def test_c_aarav_view_different_status(self, aarav_s, event_id):
        ev = _find(aarav_s.get(f"{API}/events?scope=upcoming").json(), event_id)
        assert ev is not None
        assert ev["my_rsvp_status"] == "maybe"
        assert ev["rsvp_counts"]["going"] >= 1
        assert ev["rsvp_counts"]["maybe"] >= 1

    def test_d_attendees_preview_contains_going(self, priya_s, event_id):
        ev = _find(priya_s.get(f"{API}/events?scope=upcoming").json(), event_id)
        assert isinstance(ev.get("attendees_preview"), list)
        assert 1 <= len(ev["attendees_preview"]) <= 6
        assert any("priya" in n.lower() for n in ev["attendees_preview"]), \
            f"expected 'Priya' in attendees: {ev['attendees_preview']}"

    def test_e_admin_view_matches(self, admin_s, event_id):
        r = admin_s.get(f"{API}/admin/events/{event_id}/rsvps")
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["event"]["id"] == event_id
        assert data["counts"]["going"] >= 1
        assert data["counts"]["maybe"] >= 1
        assert isinstance(data["rsvps"], list)
        for row in data["rsvps"]:
            for k in ("name", "email", "status", "updated_at"):
                assert k in row, f"missing {k}"
            assert row["status"] in ("going", "maybe", "not_going")


# ---------- Admin RSVP endpoint auth ----------
def test_admin_rsvps_requires_admin_anonymous(event_id):
    r = requests.get(f"{API}/admin/events/{event_id}/rsvps")
    assert r.status_code == 401


def test_admin_rsvps_forbidden_for_member(priya_s, event_id):
    r = priya_s.get(f"{API}/admin/events/{event_id}/rsvps")
    assert r.status_code == 403


def test_admin_rsvps_404_for_missing_event(admin_s):
    r = admin_s.get(f"{API}/admin/events/999999/rsvps")
    assert r.status_code == 404


# ---------- Response schema on /events ----------
def test_events_enriched_schema(priya_s):
    r = priya_s.get(f"{API}/events?scope=upcoming")
    assert r.status_code == 200
    rows = r.json()
    for ev in rows:
        assert "rsvp_counts" in ev
        assert set(ev["rsvp_counts"].keys()) == {"going", "maybe", "not_going"}
        assert "my_rsvp_status" in ev
        assert "attendees_preview" in ev
        assert isinstance(ev["attendees_preview"], list)
        assert len(ev["attendees_preview"]) <= 6
