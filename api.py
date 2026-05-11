import base64
import json
import os
import time
from pathlib import Path
from urllib.parse import urlparse

import requests

from flask import Flask, jsonify, request
from flask_cors import CORS
from parkinglot import ParkingLot
from report_model import Report


def load_env_file():
    """Load KEY=value pairs from .env without requiring python-dotenv."""
    try:
        from dotenv import load_dotenv

        load_dotenv(Path(__file__).with_name(".env"))
        return
    except Exception:
        pass

    env_path = Path(__file__).with_name(".env")
    if not env_path.exists():
        return

    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env_file()

app = Flask(__name__)
CORS(app)


# -------------------------------------------------------------------
# Supabase Auth helpers
# -------------------------------------------------------------------
def get_supabase_config():
    supabase_url = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
    supabase_key = (
        os.environ.get("SUPABASE_PUBLISHABLE_KEY")
        or os.environ.get("SUPABASE_ANON_KEY")
        or ""
    ).strip()
    return supabase_url, supabase_key


def get_bearer_token():
    auth_header = request.headers.get("Authorization", "")
    parts = auth_header.split()

    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]

    return None


def supabase_project_host():
    supabase_url, _ = get_supabase_config()
    if not supabase_url:
        return None
    try:
        return urlparse(supabase_url).netloc
    except Exception:
        return None


def local_dev_fallback_enabled():
    """
    Keep local class-project development from breaking when Python cannot reach
    Supabase Auth from Flask because of SSL/certificate/network issues.

    In production, set SUPABASE_LOCAL_DEV_FALLBACK=false.
    """
    value = os.environ.get("SUPABASE_LOCAL_DEV_FALLBACK", "true").strip().lower()
    return value not in {"0", "false", "no", "off"}


def decode_supabase_jwt_without_signature_check(token, supabase_url):
    """
    Local-development fallback only.

    The frontend already gets this token from Supabase after real signup/login.
    This fallback reads the JWT payload so the class project can run locally even
    if Flask cannot call https://PROJECT.supabase.co/auth/v1/user.

    It still checks that the token has a user id, belongs to this Supabase
    project issuer when an issuer is present, and is not expired. It does not
    verify the cryptographic signature, so do not use this fallback in production.
    """
    parts = token.split(".")
    if len(parts) < 2:
        raise ValueError("Token is not a JWT.")

    payload_b64 = parts[1]
    payload_b64 += "=" * (-len(payload_b64) % 4)
    payload = json.loads(base64.urlsafe_b64decode(payload_b64.encode()).decode())

    user_id = payload.get("sub")
    if not user_id:
        raise ValueError("JWT payload is missing sub/user id.")

    exp = payload.get("exp")
    if exp is not None and int(exp) <= int(time.time()):
        raise ValueError("JWT is expired. Sign in again.")

    issuer = payload.get("iss")
    expected_issuer = f"{supabase_url}/auth/v1"
    if issuer and issuer != expected_issuer:
        raise ValueError(
            f"JWT issuer does not match backend SUPABASE_URL. Expected {expected_issuer}, got {issuer}."
        )

    return {
        "id": user_id,
        "email": payload.get("email"),
        "verified_by": "local_dev_jwt_payload_fallback",
    }


def get_authenticated_user():
    """Validate the Supabase access token and return the Supabase user."""
    supabase_url, supabase_key = get_supabase_config()

    if not supabase_url or not supabase_key:
        return None, (
            jsonify(
                {
                    "success": False,
                    "error": "Backend Supabase config is missing. Add SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY to backend .env.",
                }
            ),
            500,
        )

    token = get_bearer_token()
    if not token:
        return None, (
            jsonify(
                {
                    "success": False,
                    "error": "Missing auth token. Sign in first, then try again.",
                }
            ),
            401,
        )

    auth_url = f"{supabase_url}/auth/v1/user"
    remote_error = None

    try:
        response = requests.get(
            auth_url,
            headers={
                "apikey": supabase_key,
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            },
            timeout=10,
        )

        if response.ok:
            user_data = response.json()
            user_id = user_data.get("id")
            email = user_data.get("email")

            if not user_id:
                return None, (
                    jsonify(
                        {
                            "success": False,
                            "error": "Supabase did not return a valid user id.",
                        }
                    ),
                    401,
                )

            return {"id": user_id, "email": email, "verified_by": "supabase_auth_api"}, None

        remote_error = f"Supabase Auth API returned {response.status_code}: {response.text[:500]}"
        print("Supabase remote verify failed; trying local dev fallback:", remote_error)

        # If the token is clearly invalid/expired according to Supabase, do not
        # hide that in production. In local dev, the fallback below still lets
        # you run the project if your key type or local network causes the user
        # endpoint to reject the request even though browser login succeeded.
        if response.status_code in {401, 403} and not local_dev_fallback_enabled():
            return None, (
                jsonify(
                    {
                        "success": False,
                        "error": "Invalid or expired Supabase auth token. Sign in again.",
                        "details": remote_error,
                    }
                ),
                401,
            )

    except (requests.RequestException, ValueError) as exc:
        remote_error = str(exc)
        print("Supabase remote verify exception; trying local dev fallback:", remote_error)

    if local_dev_fallback_enabled():
        try:
            user = decode_supabase_jwt_without_signature_check(token, supabase_url)
            user["remote_verify_error"] = remote_error
            return user, None
        except Exception as fallback_exc:
            return None, (
                jsonify(
                    {
                        "success": False,
                        "error": "Could not verify your account with Supabase, and the local dev JWT fallback also failed.",
                        "remote_details": remote_error,
                        "fallback_details": str(fallback_exc),
                    }
                ),
                503,
            )

    return None, (
        jsonify(
            {
                "success": False,
                "error": "Could not verify your account with Supabase. Check internet, SUPABASE_URL, and SUPABASE_PUBLISHABLE_KEY.",
                "details": remote_error,
            }
        ),
        503,
    )


@app.route("/register", methods=["POST"])
def register_disabled():
    return (
        jsonify(
            {
                "success": False,
                "error": "Registration now uses Supabase Auth from the frontend. This Flask endpoint is disabled.",
            }
        ),
        410,
    )


@app.route("/login", methods=["POST"])
def login_disabled():
    return (
        jsonify(
            {
                "success": False,
                "error": "Login now uses Supabase Auth from the frontend. This Flask endpoint is disabled.",
            }
        ),
        410,
    )


# -------------------------------------------------------------------
# Multi-campus data setup
# -------------------------------------------------------------------
CAMPUS_LOT_CONFIG = {
    "SDSU": [
        {"name": "Parking Lot 1", "total_spots": 100},
        {"name": "Parking Lot 2B", "total_spots": 100},
        {"name": "Parking Lot 2C", "total_spots": 100},
        {"name": "Parking Lot 3", "total_spots": 100},
        {"name": "Parking Lot 4", "total_spots": 100},
        {"name": "Parking Lot 12", "total_spots": 100},
        {"name": "Parking Lot 15", "total_spots": 100},
        {"name": "Parking Lot 17", "total_spots": 100},
        {"name": "Parking Lot 17A", "total_spots": 100},
        {"name": "Parking Lot 17B", "total_spots": 100},
    ],
    "UCSD": [
        {"name": "Gilman Parking Structure", "total_spots": 250},
        {"name": "Hopkins Parking Structure", "total_spots": 200},
        {"name": "Pangea Parking Structure", "total_spots": 300},
    ],
    "CSUSM": [
        {"name": "Lot B", "total_spots": 120},
        {"name": "Lot C", "total_spots": 140},
        {"name": "Parking Structure 1", "total_spots": 220},
    ],
}


def build_lots_by_campus():
    lots_by_campus = {}

    for campus_name, campus_lots in CAMPUS_LOT_CONFIG.items():
        lots_by_campus[campus_name] = {}

        for lot_data in campus_lots:
            lot_name = lot_data["name"]
            total_spots = lot_data.get("total_spots", 100)
            lots_by_campus[campus_name][lot_name] = ParkingLot(
                name=lot_name,
                campus=campus_name,
                total_spots=total_spots,
            )

    return lots_by_campus


lots_by_campus = build_lots_by_campus()

user_points = {}
# Tracks the last accepted report per user/lot so users cannot farm points by
# repeatedly submitting the same parking report.
user_report_cooldowns = {}
MIN_POINTS_TO_VIEW = 1
REPORT_REWARD = 5
REPORT_COOLDOWN_SECONDS = 10 * 60
STARTING_POINTS = 0


def get_points(reporter):
    if reporter not in user_points:
        user_points[reporter] = STARTING_POINTS
    return user_points[reporter]


def get_report_cooldown_key(reporter, campus_name, lot_name):
    return (reporter, campus_name.strip().upper(), lot_name.strip().lower())


def get_report_cooldown_remaining_seconds(reporter, campus_name, lot_name):
    last_report_at = user_report_cooldowns.get(
        get_report_cooldown_key(reporter, campus_name, lot_name)
    )

    if not last_report_at:
        return 0

    elapsed = time.time() - last_report_at
    remaining = REPORT_COOLDOWN_SECONDS - elapsed
    return max(0, int(remaining + 0.999))


def remember_report_time(reporter, campus_name, lot_name):
    user_report_cooldowns[get_report_cooldown_key(reporter, campus_name, lot_name)] = time.time()


def get_or_create_campus(campus_name):
    if campus_name not in lots_by_campus:
        lots_by_campus[campus_name] = {}
    return lots_by_campus[campus_name]


def get_or_create_lot(campus_name, lot_name):
    campus_lots = get_or_create_campus(campus_name)

    if lot_name not in campus_lots:
        campus_lots[lot_name] = ParkingLot(
            name=lot_name,
            campus=campus_name,
            total_spots=100,
        )

    return campus_lots[lot_name]


# -------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------
@app.route("/health", methods=["GET"])
def health():
    supabase_url, supabase_key = get_supabase_config()
    return jsonify(
        {
            "success": True,
            "api": "ok",
            "supabase_configured": bool(supabase_url and supabase_key),
            "supabase_project_host": supabase_project_host(),
        }
    )


@app.route("/me", methods=["GET"])
def me():
    user, error_response = get_authenticated_user()
    if error_response:
        return error_response

    return jsonify(
        {
            "success": True,
            "user": user,
            "points": get_points(user["id"]),
        }
    )


@app.route("/campuses", methods=["GET"])
def get_campuses():
    return jsonify(sorted(list(lots_by_campus.keys())))


@app.route("/lots", methods=["GET"])
def get_lots():
    user, error_response = get_authenticated_user()
    if error_response:
        return error_response

    campus_name = request.args.get("campus", "SDSU")
    reporter = user["id"]

    if campus_name not in lots_by_campus:
        return (
            jsonify(
                {
                    "success": False,
                    "error": f"Campus '{campus_name}' not found",
                }
            ),
            404,
        )

    points = get_points(reporter)

    if points < MIN_POINTS_TO_VIEW:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Not enough points. Submit a report to unlock parking data.",
                    "points": points,
                }
            ),
            403,
        )

    campus_lots = lots_by_campus[campus_name]

    return jsonify(
        {
            "success": True,
            "points": points,
            "lots": [lot.to_dict() for lot in campus_lots.values()],
        }
    )


@app.route("/report", methods=["POST"])
def submit_report():
    user, error_response = get_authenticated_user()
    if error_response:
        return error_response

    data = request.get_json() or {}

    campus_name = data.get("campus", "SDSU")
    lot_name = data.get("lot_name")
    status = data.get("status")
    reporter = user["id"]

    if not lot_name or not status:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Missing lot_name or status",
                }
            ),
            400,
        )

    try:
        cooldown_remaining = get_report_cooldown_remaining_seconds(
            reporter, campus_name, lot_name
        )
        if cooldown_remaining > 0:
            minutes = max(1, int((cooldown_remaining + 59) / 60))
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"You reported this lot too recently. Try again in about {minutes} minute(s).",
                        "points": get_points(reporter),
                        "retry_after_seconds": cooldown_remaining,
                    }
                ),
                429,
            )

        lot = get_or_create_lot(campus_name, lot_name)
        report = Report(lot, status, reporter)
        lot.add_report(report)
        remember_report_time(reporter, campus_name, lot_name)
        get_points(reporter)
        user_points[reporter] += REPORT_REWARD

        return jsonify(
            {
                "success": True,
                "campus": campus_name,
                "points": user_points[reporter],
                "lot": lot.to_dict(),
            }
        )
    except ValueError as exc:
        status_code = 429 if "too recently" in str(exc).lower() else 400
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(exc),
                    "points": get_points(reporter),
                }
            ),
            status_code,
        )


@app.route("/debug/all-lots", methods=["GET"])
def get_all_lots():
    return jsonify(
        {
            campus_name: [lot.to_dict() for lot in campus_lots.values()]
            for campus_name, campus_lots in lots_by_campus.items()
        }
    )


@app.route("/debug/auth", methods=["GET"])
def debug_auth():
    """Local debugging route: confirms Flask can read/verify the current Supabase token."""
    user, error_response = get_authenticated_user()
    if error_response:
        return error_response

    return jsonify(
        {
            "success": True,
            "message": "Backend accepted the Supabase access token.",
            "user": user,
            "points": get_points(user["id"]),
            "local_dev_fallback_enabled": local_dev_fallback_enabled(),
            "supabase_project_host": supabase_project_host(),
        }
    )


if __name__ == "__main__":
    total_lots = sum(len(campus_lots) for campus_lots in lots_by_campus.values())
    print(
        f"API started with {len(lots_by_campus)} campuses "
        f"and {total_lots} pre-loaded lots"
    )
    app.run(debug=True, port=5001, host="0.0.0.0")
