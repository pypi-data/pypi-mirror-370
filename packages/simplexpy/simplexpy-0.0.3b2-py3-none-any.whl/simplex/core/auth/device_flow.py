# simplex/core/auth/device_flow.py

import time
import json
import requests
from pathlib import Path
import simplex
from simplex.core.config.auth import get_auth_config
import webbrowser

TOKEN_FILE = Path.home() / ".simplex" / "token.json"

def login(auto_open_browser: bool = True):
    auth_config = get_auth_config()
    device_code_url = f"https://{auth_config['domain']}/oauth/device/code"
    token_url = f"https://{auth_config['domain']}/oauth/token"

    # Step 1: Request device code
    response = requests.post(device_code_url, data={
        "client_id": auth_config["client_id"],
        "scope": auth_config["scope"],
        "audience": auth_config["audience"]
    })

    if response.status_code != 200:
        print("❌ Failed to start device flow")
        print(response.json())
        return

    result = response.json()
    verification_url = result["verification_uri_complete"]
    print(f"\n🔑 Visit: {result['verification_uri_complete']}")
    print("⏳ Waiting for authorization...\n")

    if auto_open_browser:
        try:
            webbrowser.open(verification_url)
            print("🌐 Browser opened automatically.")
        except Exception:
            print("⚠️ Could not open browser. Please open the URL manually.")

    payload = {
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        "device_code": result["device_code"],
        "client_id": auth_config["client_id"]
    }

    start_time = time.time()
    interval = result.get("interval", 1)
    expires_in = 30  # in seconds

    while (time.time() - start_time) < expires_in:
        time.sleep(interval)
        token_response = requests.post(token_url, data=payload)

        if token_response.status_code == 200:
            token_data = token_response.json()
            TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(TOKEN_FILE, "w") as f:
                json.dump(token_data, f)
            print("✅ Login successful. Token saved to:", TOKEN_FILE)
            return

        if token_response.status_code == 400:
            error = token_response.json().get("error")
            if error == "authorization_pending":
                print("⏳ Still waiting for user to complete login...")
                continue
            elif error == "slow_down":
                interval += 5
                print("⚠️ Server asked to slow down. Increasing polling interval.")
                continue
            else:
                print(f"❌ Login failed: {error}")
                return
            
        if token_response.status_code == 403:
            continue

        print("❌ Unexpected error:", token_response.text)
        return
    print("⏱️ Timed out. Try again.")


def logout():
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()
        print("✅ Logged out")
    else:
        print("ℹ️ No active session found")


def get_access_token() -> str:
    if not TOKEN_FILE.exists():
        raise Exception(f"{simplex.core.error.handling.RED}❌ Not logged in. Please run `simplex auth login`. {simplex.core.error.handling.RESET}")
    with open(TOKEN_FILE) as f:
        return json.load(f)["access_token"]

if __name__ == "__main__":
    login()
    #logout()