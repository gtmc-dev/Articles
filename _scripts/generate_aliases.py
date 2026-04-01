#!/usr/bin/env python3

import re
import subprocess
import urllib.request
import json
import yaml
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
MANUAL_ALIASES_FILE = SCRIPT_DIR / "authors_alias_manual.yml"

GITHUB_NOREPLY_PATTERN = re.compile(r"\+(\w+)@users\.noreply\.github\.com")
GITHUB_API_BASE = "https://api.github.com"


def get_git_authors() -> list[tuple[str, str]]:
    result = subprocess.run(
        ["git", "log", "--all", "--format=%an <%ae>"],
        capture_output=True,
        text=True,
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


def extract_github_username_from_email(email: str) -> str | None:
    match = GITHUB_NOREPLY_PATTERN.search(email)
    if match:
        return match.group(1)
    return None


def fetch_github_login_from_email(email: str) -> str | None:
    try:
        url = f"{GITHUB_API_BASE}/search/users?q={email}+in:email"
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "gtmc-alias-script",
            },
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            if data.get("total_count", 0) > 0:
                return data["items"][0].get("login")
    except Exception:
        pass
    return None


def get_github_username_for_email(email: str) -> str | None:
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

    email_to_github_username: dict[str, str] = {}
    for email in email_to_display_names:
        username = get_github_username_for_email(email)
        if username:
            email_to_github_username[email] = username

    display_name_to_canonical: dict[str, str] = {}
    for email, display_names in email_to_display_names.items():
        display_names = list(display_names)
        if len(display_names) == 1:
            name = display_names[0]
            display_name_to_canonical[name] = email_to_github_username.get(
                email, name)
        else:
            github_username = email_to_github_username.get(email)
            if github_username:
                for name in display_names:
                    display_name_to_canonical[name] = github_username
            else:
                canonical = display_names[0]
                for name in display_names:
                    display_name_to_canonical[name] = canonical

    canonical_to_display_names: dict[str, set[str]] = {}
    for display_name, canonical in display_name_to_canonical.items():
        if canonical not in canonical_to_display_names:
            canonical_to_display_names[canonical] = set()
        canonical_to_display_names[canonical].add(display_name)

    aliases_by_canonical: dict[str, list[str]] = {}
    for canonical, display_names in canonical_to_display_names.items():
        if len(display_names) > 1:
            aliases_by_canonical[canonical] = sorted(
                d for d in display_names if d != canonical
            )

    return dict(sorted(aliases_by_canonical.items()))


def main():
    auto_aliases = generate_aliases()
    manual_aliases = load_manual_aliases()
    aliases = merge_aliases(auto_aliases, manual_aliases)

    with open(SCRIPT_DIR / "authors_alias.yml", "w", encoding="utf-8") as f:
        yaml.dump(
            aliases, f, allow_unicode=True, default_flow_style=False, sort_keys=False
        )

    print(f"Generated authors_alias.yml with {len(aliases)} canonical authors")


if __name__ == "__main__":
    main()
