"""
Bootstrap / Refresh Script for Browser Sessions
=================================================
Yeh script ek naya authenticated session banata hai Playwright se
aur usse Session Manager API mein save karta hai.

Kaise use karein:
1. profile_key, platform, login_url set karo neeche
2. Yeh script Browserless se connect hoga, browser kholega
3. Manual login karna hoga (ya pre-filled credentials se)
4. Session save ho jayega Session Manager mein

Run karne ka tarika (Playwright worker container ke andar se):
python3 bootstrap-session.py --profile_key facebook_page1 --platform facebook --login_url https://facebook.com/login
"""

import argparse
import json
import urllib.request
from playwright.sync_api import sync_playwright

BROWSERLESS_URL = "ws://browserless:3000?token=social_browserless_token_123456"
SESSION_MANAGER_URL = "http://session-manager:8767"


def bootstrap_session(profile_key, platform, login_url, account_name=None):
    print(f"Connecting to Browserless for profile: {profile_key}")

    with sync_playwright() as p:
        browser = p.chromium.connect(BROWSERLESS_URL)
        context = browser.new_context()
        page = context.new_page()

        print(f"Opening login page: {login_url}")
        page.goto(login_url)

        print("=" * 60)
        print("MANUAL LOGIN REQUIRED")
        print("Browser session is open. Please complete login manually")
        print("via the Browserless live view, then press Enter here")
        print("to continue and save the session.")
        print("=" * 60)
        input("Press Enter once logged in...")

        storage_state = context.storage_state()

        print("Saving session to Session Manager...")
        data = json.dumps({
            "storage_state": storage_state,
            "platform": platform,
            "account_name": account_name or profile_key
        }).encode()

        req = urllib.request.Request(
            f"{SESSION_MANAGER_URL}/session/{profile_key}",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        res = urllib.request.urlopen(req)
        print("Saved:", res.read().decode())

        context.close()
        browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile_key", required=True)
    parser.add_argument("--platform", required=True)
    parser.add_argument("--login_url", required=True)
    parser.add_argument("--account_name", required=False)
    args = parser.parse_args()

    bootstrap_session(args.profile_key, args.platform, args.login_url, args.account_name)
