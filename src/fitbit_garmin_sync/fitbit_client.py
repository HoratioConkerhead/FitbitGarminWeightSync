from __future__ import annotations

import json
import threading
import traceback
import webbrowser
from datetime import date, datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

import fitbit

from .config import ensure_data_dir
from .models import WeightEntry


TOKEN_FILE_NAME = "fitbit_tokens.json"


def _token_file():
    return ensure_data_dir() / TOKEN_FILE_NAME


def _save_tokens(token_dict: dict) -> None:
    _token_file().write_text(json.dumps(token_dict, indent=2))


def _load_tokens() -> dict | None:
    path = _token_file()
    if path.exists():
        return json.loads(path.read_text())
    return None


class _OAuthCallbackHandler(BaseHTTPRequestHandler):
    auth_code: str | None = None

    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        _OAuthCallbackHandler.auth_code = query.get("code", [None])[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h1>Authorization successful!</h1><p>You can close this tab.</p>")

    def log_message(self, format, *args):
        pass  # suppress request logging


def _do_oauth_flow(client_id: str, client_secret: str) -> fitbit.Fitbit:
    redirect_uri = "http://127.0.0.1:8080/"
    scopes = ["weight"]

    oauth = fitbit.Fitbit(
        client_id,
        client_secret,
        redirect_uri=redirect_uri,
        timeout=30,
    )

    auth_url, _ = oauth.client.authorize_token_url(scope=scopes)

    server = HTTPServer(("127.0.0.1", 8080), _OAuthCallbackHandler)
    server_thread = threading.Thread(target=server.handle_request)
    server_thread.start()

    print(f"Opening browser for Fitbit authorization...")
    print(f"If the browser doesn't open, visit: {auth_url}")
    webbrowser.open(auth_url)

    server_thread.join(timeout=120)
    server.server_close()

    code = _OAuthCallbackHandler.auth_code
    if not code:
        raise SystemExit("Failed to receive authorization code from Fitbit.")

    try:
        oauth.client.fetch_access_token(code)
    except Exception:
        traceback.print_exc()
        raise SystemExit("Failed to exchange authorization code for tokens.")

    token_dict = {
        "access_token": oauth.client.session.token["access_token"],
        "refresh_token": oauth.client.session.token["refresh_token"],
    }
    _save_tokens(token_dict)
    print("Fitbit authorization complete. Tokens saved.")

    return fitbit.Fitbit(
        client_id,
        client_secret,
        access_token=token_dict["access_token"],
        refresh_token=token_dict["refresh_token"],
        refresh_cb=_save_tokens,
        system=fitbit.Fitbit.METRIC,
    )


def get_fitbit_client(client_id: str, client_secret: str) -> fitbit.Fitbit:
    tokens = _load_tokens()
    if tokens:
        return fitbit.Fitbit(
            client_id,
            client_secret,
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            refresh_cb=_save_tokens,
            system=fitbit.Fitbit.METRIC,
        )
    return _do_oauth_flow(client_id, client_secret)


def fetch_weight_entries(
    client: fitbit.Fitbit, start_date: date, end_date: date
) -> list[WeightEntry]:
    entries = []
    current = start_date
    while current <= end_date:
        # Fitbit API: get weight logs for a single date
        data = client.get_bodyweight(base_date=current, period="1d")
        for record in data.get("weight", []):
            timestamp = datetime.strptime(
                f"{record['date']} {record.get('time', '00:00:00')}",
                "%Y-%m-%d %H:%M:%S",
            )
            entries.append(
                WeightEntry(
                    log_id=str(record["logId"]),
                    timestamp=timestamp,
                    weight_kg=record["weight"],
                    body_fat_pct=record.get("fat"),
                    bmi=record.get("bmi"),
                )
            )
        current += timedelta(days=1)
    return entries
