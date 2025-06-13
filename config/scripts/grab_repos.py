#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx"]
# ///

import os
import sys
import httpx

token = os.getenv("GITHUB_TOKEN")
if not token:
    print("❌ GITHUB_TOKEN not found in environment.", file=sys.stderr)
    sys.exit(1)

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

url = "https://api.github.com/user/repos"
params = {"per_page": 100, "page": 1}

print("📡 Fetching repositories...")

with httpx.Client(headers=headers) as client:
    while True:
        resp = client.get(url, params=params)
        resp.raise_for_status()
        repos = resp.json()

        if not repos:
            break

        for repo in repos:
            print(f"🔗 {repo['clone_url']}")

        params["page"] += 1
