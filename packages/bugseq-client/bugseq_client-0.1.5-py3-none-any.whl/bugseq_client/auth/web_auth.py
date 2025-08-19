import contextlib
import logging
import threading
import time
import webbrowser
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

import requests
from authlib.integrations.requests_client import OAuth2Session

logger = logging.getLogger(__name__)


@dataclass
class OAuthConfig:
    client_id: str
    redirect_uri: str

    app_name: str = "bugseq"
    scope: list[str] = field(default_factory=lambda: ["email", "openid"])
    client_secret: str | None = None
    open_browser: bool = True
    auth_timeout_seconds: int = 300
    authority: str | None = None
    callback_listen_host: str = "localhost"

    # The following are discovered from the authority
    authorize_url: str | None = field(default=None, init=False)
    token_url: str | None = field(default=None, init=False)

    def __post_init__(self):
        if self.authority:
            self._discover()

    def _discover(self):
        """Fetch OIDC configuration from the authority."""
        if not self.authority:
            return
        # clean up authority URL
        if not self.authority.startswith("https://"):
            self.authority = "https://" + self.authority
        if self.authority.endswith("/"):
            self.authority = self.authority[:-1]

        url = f"{self.authority}/.well-known/openid-configuration"
        try:
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            self.authorize_url = data["authorization_endpoint"]
            self.token_url = data["token_endpoint"]
        except requests.exceptions.RequestException as e:
            raise RuntimeError(
                f"Failed to discover OIDC configuration from {url}: {e}"
            ) from e


DEFAULT_OAUTH_CONFIG = OAuthConfig(
    client_id="1nda6286pu7o5uo84ikg6omnig",
    client_secret=None,  # or None for public clients
    redirect_uri="http://localhost:8411/bugseq/cognito/login",
    authority="https://cognito-idp.us-west-2.amazonaws.com/us-west-2_T0zTTgjFc",
)


class _CodeReceiver(BaseHTTPRequestHandler):
    # Shared container for the auth code
    code_container: dict[str, str | None] = {
        "code": None,
        "error": None,
        "error_description": None,
    }

    def do_GET(self):  # noqa: N802
        parsed = urlparse(self.path)
        if not parsed.path.startswith("/bugseq/"):
            self._not_found()
            return

        qs = parse_qs(parsed.query)
        if "error" in qs:
            _CodeReceiver.code_container["error"] = qs.get("error", ["unknown_error"])[
                0
            ]
            _CodeReceiver.code_container["error_description"] = qs.get(
                "error_description", [None]
            )[0]
        _CodeReceiver.code_container["code"] = qs.get("code", [None])[0]
        self._ok()

    def log_message(self, format: str, *args):  # silence default server logs
        return

    def _ok(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(
            b"""\
<html>
    <body>
        <h2>Login complete. You can close this window.</h2>
    </body>
</html>\
"""
        )

    def _not_found(self):
        self.send_response(404)
        self.end_headers()


def run_web_flow_for_token(cfg: OAuthConfig) -> dict:
    """
    Start a loopback HTTP server to catch the authorization code, then exchange for
    tokens. Uses PKCE (S256). Returns the full token dict from the provider.
    """

    # Prepare auth session (Authlib will retain PKCE verifier within the session)
    session = OAuth2Session(
        cfg.client_id,
        cfg.client_secret,
        scope=cfg.scope,
        redirect_uri=cfg.redirect_uri,
        # Extra security: PKCE
        code_challenge_method="S256",
    )

    auth_url, _state = session.create_authorization_url(cfg.authorize_url)

    listen_hostname = cfg.callback_listen_host
    parsed_callback_uri = urlparse(cfg.redirect_uri)
    if not parsed_callback_uri.port:
        raise ValueError(f"No callback port found in redirect_uri={cfg.redirect_uri}")

    # Fire up a local HTTP server to catch the redirect
    httpd = HTTPServer((listen_hostname, parsed_callback_uri.port), _CodeReceiver)
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()

    if cfg.open_browser:
        with contextlib.suppress(Exception):
            webbrowser.open(auth_url)

    # If the browser didn't open, print the URL for the user to click
    print(f"Please complete login by visiting:\n{auth_url}\n")

    # Wait for the code or timeout
    started = time.time()
    try:
        while time.time() - started < cfg.auth_timeout_seconds:
            if _CodeReceiver.code_container["error"]:
                err_msg = _CodeReceiver.code_container["error"]
                if _CodeReceiver.code_container["error_description"]:
                    err_msg += f': {_CodeReceiver.code_container["error_description"]}'
                raise RuntimeError(f"Authorization error: {err_msg}")
            if _CodeReceiver.code_container["code"]:
                break

            time.sleep(0.15)
    finally:
        httpd.shutdown()

    code = _CodeReceiver.code_container["code"]
    _CodeReceiver.code_container = {
        "code": None,
        "error": None,
    }  # reset for future runs

    if not code:
        raise TimeoutError("Timed out waiting for authorization code; try again.")

    # Exchange code for tokens
    token = session.fetch_token(
        cfg.token_url,
        code=code,
    )
    return token
