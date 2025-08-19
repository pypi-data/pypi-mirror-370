from __future__ import annotations

import json
import os
import sys
import threading
import time
import queue
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
import webbrowser

import bsapi
import bsapi.helper
from bsapi import oauth

REQUIRED_SCOPES = "core:*:* grades:*:* groups:*:* quizzing:*:*"

LOCALHOST_PORT = 8731  # Localhost port for OAuth callback (should be free and not used by other services)


class TokenManager:
    """Manages OAuth token storage and retrieval."""

    def __init__(self, token_file: Path):
        self.token_file = token_file
        self.token_file.parent.mkdir(parents=True, exist_ok=True)

    def get_token(self) -> Optional[str]:
        """Get token from env var or file."""
        if token := os.environ.get("BSCLI_ACCESS_TOKEN"):
            return token

        if self.token_file.exists():
            try:
                data = json.loads(self.token_file.read_text())
                return data.get("access_token")
            except:
                pass
        return None

    def save_token(self, token: str):
        """Save token to file."""
        self.token_file.write_text(json.dumps({"access_token": token}))
        self.token_file.chmod(0o600)


class CallbackHandler(BaseHTTPRequestHandler):
    """Handles OAuth callback and extracts authorization code."""

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if "code" in params:
            self.server.auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET")
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"""
                <html><body>
                    <h1>Authorization successful!</h1>
                    <p>You can close this window.</p>
                    <script>window.close();</script>
                </body></html>
            """
            )
        elif "error" in params:
            self.server.auth_error = params["error"][0]
            self.send_response(400)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET")
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(
                f"""
                <html><body>
                    <h1>Authorization failed</h1>
                    <p>Error: {params['error'][0]}</p>
                </body></html>
            """.encode()
            )
        else:
            self.send_response(400)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET")
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Invalid request</h1></body></html>")

    def log_message(self, format, *args):
        # Suppress HTTP server logs
        pass


def perform_oauth_interactive(api_config: bsapi.APIConfig) -> Optional[str]:
    """Try automatic OAuth flow with localhost server, with manual fallback."""
    result_queue = queue.Queue()

    def run_server():
        try:
            server = HTTPServer(("localhost", LOCALHOST_PORT), CallbackHandler)
            server.auth_code = None
            server.auth_error = None

            # Start server
            server_thread = threading.Thread(target=server.serve_forever, daemon=True)
            server_thread.start()

            # Wait for callback
            timeout = 120  # 2 minutes
            start_time = time.time()

            while server.auth_code is None and server.auth_error is None:
                if time.time() - start_time > timeout:
                    break
                time.sleep(0.1)

            if server.auth_code:
                result_queue.put(("code", server.auth_code))
            elif server.auth_error:
                result_queue.put(("error", server.auth_error))

            server.shutdown()
            server.server_close()

        except Exception as e:
            result_queue.put(("error", str(e)))

    def get_manual_input():
        try:
            print("\nAlternatively, paste the authorization code here:")
            code = input(
                "Authorization code (or press Enter to wait for browser): "
            ).strip()
            if code:
                result_queue.put(("code", code))
        except KeyboardInterrupt:
            result_queue.put(("error", "Cancelled by user"))

    try:
        auth_url = oauth.create_auth_url(
            api_config.client_id, api_config.redirect_uri, scope=REQUIRED_SCOPES
        )

        print(f"Opening browser for authorization...")
        try:
            webbrowser.open(auth_url)
            print("Waiting for authorization via browser...")
        except Exception:  # noqa
            print("❌ Unable to open browser automatically")
            print(f"Please manually open this URL in your browser:")
            print(f"{auth_url}")
            print("Waiting for authorization...")

        # Start both server and manual input concurrently
        server_thread = threading.Thread(target=run_server, daemon=True)
        manual_thread = threading.Thread(target=get_manual_input, daemon=True)

        server_thread.start()
        manual_thread.start()

        # Wait for first result
        try:
            result_type, result_value = result_queue.get(
                timeout=130
            )  # Slightly longer than server timeout
        except queue.Empty:
            print("Authorization timed out")
            return None

        if result_type == "error":
            raise ValueError(result_value)

        code = result_value
        print("✅ Authorization code received")

        # Exchange code for token
        token_response = oauth.exchange_code_for_token(
            api_config.client_id,
            api_config.client_secret,
            api_config.redirect_uri,
            code,
        )

        return token_response["access_token"]

    except Exception as e:
        print(f"Automatic flow failed: {e}")
        return None


def perform_oauth_manual(api_config: bsapi.APIConfig) -> str:
    """Fallback manual OAuth flow."""

    auth_url = oauth.create_auth_url(
        api_config.client_id, api_config.redirect_uri, scope=REQUIRED_SCOPES
    )

    print(f"Authorization URL: {auth_url}")
    print("Please open the URL above in your browser and complete authorization.")
    print(f"\nAfter authorization, you'll be redirected to {api_config.redirect_uri}")
    print("Copy the authorization code from the page and paste it below:")

    while True:
        code = input("Authorization code: ").strip()
        if not code:
            print("Please enter the authorization code")
            continue

        try:
            # Exchange code for token
            token_response = oauth.exchange_code_for_token(
                api_config.client_id,
                api_config.client_secret,
                api_config.redirect_uri,
                code,
            )

            return token_response["access_token"]

        except ValueError as e:
            print(f"❌ Error: {e}")
            print("Please try again with the correct authorization code.")
        except bsapi.APIError as e:
            print(f"❌ Token exchange failed: {e}")
            sys.exit(1)
