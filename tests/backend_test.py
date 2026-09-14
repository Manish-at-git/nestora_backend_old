"""
Nestora — end-to-end backend API tests.
Covers: public onboarding flow (code → verify → create-account),
        request-code + admin approval,
        update-details request + admin resolve,
        admin auth guard + full admin CRUD.
"""
import os
import re
import time
import uuid
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://nestora-code-auth.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"

ADMIN_EMAIL = "admin@nestora.io"
ADMIN_PASSWORD = "Admin@Nestora2026"


# ---------- Fixtures ----------
@pytest.fixture(scope="session")
def s():
    sess = requests.Session()
    sess.headers.update({"Content-Type": "application/json"})
    return sess


@pytest.fixture(scope="session")
def admin_token(s):
    r = s.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert r.status_code == 200, f"admin login failed: {r.status_code} {r.text}"
    data = r.json()
    assert data["account"]["role"] == "admin"
    assert isinstance(data["token"], str) and len(data["token"]) > 10
    return data["token"]


@pytest.fixture(scope="session")
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}


# ---------- Health ----------
def test_root(s):
    r = s.get(f"{API}/")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


# ---------- login-code ----------
def test_login_code_invalid_format(s):
    r = s.post(f"{API}/login-code", json={"code": "bad"})
    assert r.status_code == 400


def test_login_code_not_found(s):
    r = s.post(f"{API}/login-code", json={"code": "BADCODE1"})
    assert r.status_code == 404
    assert "Invalid" in r.json()["detail"]


def test_login_code_valid_demo3(s):
    """Use DEMO3 to preserve DEMO1/2 for onboarding + update flows."""
    r = s.post(f"{API}/login-code", json={"code": "NST-DEMO3"})
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["valid"] is True
    assert "code_id" in data
    assert data["already_registered"] is False


# ---------- user-details ----------
def test_user_details_demo1(s):
    r = s.get(f"{API}/user-details", params={"code": "NST-DEMO1"})
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "Aarav Sharma"
    assert "Marigold" in data["address"]
    assert data["email"] == "aarav.demo@nestora.io"


def test_user_details_missing(s):
    r = s.get(f"{API}/user-details", params={"code": "NONEXIST"})
    assert r.status_code == 404


# ---------- create-account (password strength) ----------
def test_create_account_weak_password_short(s):
    r = s.post(f"{API}/create-account", json={
        "code": "NST-DEMO1", "email": "aarav.demo@nestora.io",
        "password": "abc", "confirm_password": "abc"
    })
    assert r.status_code == 400
    assert "8 characters" in r.json()["detail"]


def test_create_account_weak_no_upper(s):
    r = s.post(f"{API}/create-account", json={
        "code": "NST-DEMO1", "email": "aarav.demo@nestora.io",
        "password": "nestora@2026", "confirm_password": "nestora@2026"
    })
    assert r.status_code == 400
    assert "uppercase" in r.json()["detail"].lower()


def test_create_account_weak_no_digit(s):
    r = s.post(f"{API}/create-account", json={
        "code": "NST-DEMO1", "email": "aarav.demo@nestora.io",
        "password": "Nestora@Pass", "confirm_password": "Nestora@Pass"
    })
    assert r.status_code == 400
    assert "number" in r.json()["detail"].lower()


def test_create_account_weak_no_symbol(s):
    r = s.post(f"{API}/create-account", json={
        "code": "NST-DEMO1", "email": "aarav.demo@nestora.io",
        "password": "Nestora2026", "confirm_password": "Nestora2026"
    })
    assert r.status_code == 400
    assert "special" in r.json()["detail"].lower()


def test_create_account_mismatch(s):
    r = s.post(f"{API}/create-account", json={
        "code": "NST-DEMO1", "email": "aarav.demo@nestora.io",
        "password": "Nestora@2026", "confirm_password": "Nestora@2027"
    })
    assert r.status_code == 400
    assert "match" in r.json()["detail"].lower()


# ---------- Full onboarding + login roundtrip on DEMO1 ----------
class TestOnboardingAarav:
    """Uses NST-DEMO1 end-to-end: validate → details → create account → login → me."""

    def test_a_validate(self, s):
        r = s.post(f"{API}/login-code", json={"code": "NST-DEMO1"})
        # Might already be used from prior run — if so skip class
        if r.status_code != 200:
            pytest.skip(f"NST-DEMO1 not active (status={r.status_code}) — likely used by earlier run")
        assert r.json()["valid"] is True

    def test_b_create_account(self, s):
        r = s.post(f"{API}/create-account", json={
            "code": "NST-DEMO1",
            "email": "aarav.demo@nestora.io",
            "password": "Nestora@2026",
            "confirm_password": "Nestora@2026",
        })
        if r.status_code == 409:
            pytest.skip("Account already exists — skipping create-account tests")
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["ok"] is True
        assert data["account"]["email"] == "aarav.demo@nestora.io"
        assert data["account"]["role"] == "member"
        assert isinstance(data["token"], str) and len(data["token"]) > 10
        # token persists
        pytest.aarav_token = data["token"]

    def test_c_code_now_used(self, s):
        r = s.post(f"{API}/login-code", json={"code": "NST-DEMO1"})
        # Either 400 (no longer active) or 200 with already_registered True
        if r.status_code == 200:
            assert r.json()["already_registered"] is True
        else:
            assert r.status_code == 400

    def test_d_login_email_password(self, s):
        r = s.post(f"{API}/auth/login", json={
            "email": "aarav.demo@nestora.io", "password": "Nestora@2026"
        })
        assert r.status_code == 200
        data = r.json()
        assert data["account"]["role"] == "member"
        pytest.aarav_token = data["token"]

    def test_e_me_endpoint(self, s):
        tok = getattr(pytest, "aarav_token", None)
        if not tok:
            pytest.skip("no member token")
        r = s.get(f"{API}/auth/me", headers={"Authorization": f"Bearer {tok}"})
        assert r.status_code == 200
        d = r.json()
        assert d["account"]["email"] == "aarav.demo@nestora.io"
        assert d["profile"]["name"] == "Aarav Sharma"

    def test_f_wrong_password(self, s):
        r = s.post(f"{API}/auth/login", json={
            "email": "aarav.demo@nestora.io", "password": "wrongPassword@1"
        })
        assert r.status_code == 401

    def test_g_member_cannot_hit_admin(self, s):
        tok = getattr(pytest, "aarav_token", None)
        if not tok:
            pytest.skip("no member token")
        r = s.get(f"{API}/admin/stats", headers={"Authorization": f"Bearer {tok}"})
        assert r.status_code == 403


# ---------- Request-code flow + Admin approval ----------
class TestCodeRequestAdminFlow:
    unique_email = f"test.request.{uuid.uuid4().hex[:8]}@nestora.io"

    def test_a_submit_request(self, s):
        r = s.post(f"{API}/request-code", json={
            "name": "TEST Applicant",
            "email": self.unique_email,
            "contact_number": "+91-9000000001",
        })
        assert r.status_code == 200
        assert r.json()["ok"] is True

    def test_b_duplicate_pending_rejected(self, s):
        r = s.post(f"{API}/request-code", json={
            "name": "TEST Applicant",
            "email": self.unique_email,
            "contact_number": "+91-9000000001",
        })
        assert r.status_code == 409

    def test_c_admin_list_and_approve(self, s, admin_headers):
        r = s.get(f"{API}/admin/code-requests", headers=admin_headers)
        assert r.status_code == 200
        rows = r.json()
        target = next((x for x in rows if x["email"] == self.unique_email), None)
        assert target, f"submitted request not found in list"
        assert target["status"] == "pending"
        req_id = target["id"]

        r = s.post(f"{API}/admin/code-requests/approve",
                   json={"request_id": req_id}, headers=admin_headers)
        assert r.status_code == 200
        issued = r.json()["issued_code"]
        assert issued.startswith("NST-")
        pytest.issued_code = issued
        pytest.issued_req_id = req_id

    def test_d_issued_code_listed(self, s, admin_headers):
        r = s.get(f"{API}/admin/codes", headers=admin_headers)
        assert r.status_code == 200
        codes = [c["login_code"] for c in r.json()]
        assert getattr(pytest, "issued_code", "-") in codes

    def test_e_double_approve_fails(self, s, admin_headers):
        r = s.post(f"{API}/admin/code-requests/approve",
                   json={"request_id": pytest.issued_req_id}, headers=admin_headers)
        assert r.status_code == 400


# ---------- Update-details request + resolve ----------
class TestUpdateDetailsFlow:
    def test_a_submit_update(self, s):
        r = s.post(f"{API}/update-details-request", json={
            "code": "NST-DEMO2",
            "requested_address": "New address 42, Mumbai, MH 400051",
            "note": "TEST correction from automated test",
        })
        assert r.status_code == 200

    def test_b_admin_lists(self, s, admin_headers):
        r = s.get(f"{API}/admin/update-requests", headers=admin_headers)
        assert r.status_code == 200
        rows = r.json()
        target = next((x for x in rows if x["note"] == "TEST correction from automated test"), None)
        assert target is not None
        assert target["status"] == "open"
        pytest.update_req_id = target["id"]

    def test_c_resolve(self, s, admin_headers):
        r = s.post(f"{API}/admin/update-requests/{pytest.update_req_id}/resolve",
                   headers=admin_headers)
        assert r.status_code == 200
        # Verify persisted
        r2 = s.get(f"{API}/admin/update-requests", headers=admin_headers)
        target = next((x for x in r2.json() if x["id"] == pytest.update_req_id), None)
        assert target["status"] == "resolved"


# ---------- Admin protection ----------
def test_admin_stats_unauth(s):
    r = requests.get(f"{API}/admin/stats")
    assert r.status_code == 401


def test_admin_stats_admin(s, admin_headers):
    r = s.get(f"{API}/admin/stats", headers=admin_headers)
    assert r.status_code == 200
    d = r.json()
    for k in ["total_codes", "used_codes", "pending_requests", "members", "open_update_requests"]:
        assert k in d
        assert isinstance(d[k], int)


def test_admin_create_member_inline(s, admin_headers):
    email = f"TEST_inline.{uuid.uuid4().hex[:8]}@nestora.io"
    r = s.post(f"{API}/admin/members", headers=admin_headers, json={
        "name": "TEST Inline Member",
        "address": "1 TEST street, City 000000",
        "email": email,
        "contact_number": "+91-9111100000",
    })
    assert r.status_code == 200
    code = r.json()["issued_code"]
    assert code.startswith("NST-")
    # verify listed
    r2 = s.get(f"{API}/admin/codes", headers=admin_headers)
    all_codes = [c["login_code"] for c in r2.json()]
    assert code in all_codes


def test_admin_email_log(s, admin_headers):
    r = s.get(f"{API}/admin/emails", headers=admin_headers)
    assert r.status_code == 200
    rows = r.json()
    assert isinstance(rows, list)
    # Should have accumulated emails from earlier flows
    assert len(rows) >= 1
    subs = " ".join(x["subject"] for x in rows)
    assert "Nestora" in subs
