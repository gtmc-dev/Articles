#!/usr/bin/env python3

import json
import re
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional

import yaml

SCRIPT_DIR = Path(__file__).parent
MANUAL_ALIASES_FILE = SCRIPT_DIR / "authors_alias_override.yml"

GITHUB_NOREPLY_PATTERN = re.compile(r"\+(\w+)@users\.noreply\.github\.com")
GITHUB_API_BASE = "https://api.github.com"


def get_git_authors() -> list[tuple[str, str]]:
    result = subprocess.run(
        ["git", "log", "--all", "--format=%an <%ae>"],
        capture_output=True,
        text=True,
        check=False,
        encoding="utf-8",
    )

    if result.returncode != 0:
        return []

    authors = []
    for line in result.stdout.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        match = re.match(r"(.+) <(.+)>", line)
        if match:
            display_name, email = match.groups()
            authors.append((display_name, email))
    return authors


def extract_github_username_from_email(email: str) -> Optional[str]:
    match = GITHUB_NOREPLY_PATTERN.search(email)
    if match:
        return match.group(1)
    return None


def fetch_github_login_from_email(email: str) -> Optional[str]:
    try:
        url = f"{GITHUB_API_BASE}/repos/gtmc-dev/articles/commits?author={email}&per_page=1"
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "gtmc-alias-script",
            },
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            if data:
                return data[0].get("author", {}).get("login")
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        pass
    return None


def get_github_username_for_email(email: str) -> Optional[str]:
    username = extract_github_username_from_email(email)
    if username:
        return username
    username = fetch_github_login_from_email(email)
    if username:
        return username
    return None


def load_manual_aliases() -> dict[str, list[str]]:
    if not MANUAL_ALIASES_FILE.exists():
        return {}
    return yaml.safe_load(MANUAL_ALIASES_FILE.read_text(encoding="utf-8")) or {}


def merge_aliases(
    auto_aliases: dict[str, list[str]], manual_aliases: dict[str, list[str]]
) -> dict[str, list[str]]:
    merged = auto_aliases.copy()
    for canonical, aliases in manual_aliases.items():
        if canonical in merged:
            for alias in aliases:
                if alias not in merged[canonical]:
                    merged[canonical].append(alias)
            merged[canonical] = sorted(set(merged[canonical]))
        else:
            merged[canonical] = sorted(aliases)
    return dict(sorted(merged.items()))


def generate_aliases() -> dict[str, list[str]]:
    authors = get_git_authors()

    email_to_display_names: dict[str, set[str]] = {}
    for display_name, email in authors:
        if email not in email_to_display_names:
            email_to_display_names[email] = set()
        email_to_display_names[email].add(display_name)

    github_username_to_emails: dict[str, set[str]] = {}
    for email in email_to_display_names.keys():
        github_username = get_github_username_for_email(email)
        if github_username:
            if github_username not in github_username_to_emails:
                github_username_to_emails[github_username] = set()
            github_username_to_emails[github_username].add(email)

    aliases_by_canonical: dict[str, list[str]] = {}
    for github_username, emails in github_username_to_emails.items():
        display_names = set()
        for email in emails:
            display_names.update(email_to_display_names.get(email, []))
        canonical = github_username
        aliases = set(display_names) - {canonical}
        if aliases:
            aliases_by_canonical[canonical] = sorted(aliases)

    return dict(aliases_by_canonical.items())


def main():
    auto_aliases = generate_aliases()
    manual_aliases = load_manual_aliases()
    aliases = merge_aliases(auto_aliases, manual_aliases)

    with open(SCRIPT_DIR / "authors_alias.yml", "w", encoding="utf-8") as f:
        yaml.dump(
            aliases,
            f,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
            indent=2,
        )

    print(f"Generated authors_alias.yml with {len(aliases)} canonical authors")


if __name__ == "__main__":
    main()
