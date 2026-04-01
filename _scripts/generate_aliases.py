#!/usr/bin/env python3

import re
import subprocess
import yaml
from collections import Counter
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

GITHUB_NOREPLY_PATTERN = re.compile(r"\+(\w+)@users\.noreply\.github\.com")


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


def extract_github_username(email: str) -> str | None:
    match = GITHUB_NOREPLY_PATTERN.search(email)
    if match:
        return match.group(1)
    return None


def group_by_email(
    authors: list[tuple[str, str]],
) -> dict[str, list[tuple[str, str]]]:
    email_groups = {}
    for display_name, email in authors:
        if email not in email_groups:
            email_groups[email] = []
        email_groups[email].append((display_name, email))
    return email_groups


def generate_aliases() -> dict[str, list[str]]:
    authors = get_git_authors()
    email_groups = group_by_email(authors)

    email_to_github_username: dict[str, str | None] = {}
    for email in email_groups:
        email_to_github_username[email] = extract_github_username(email)

    canonical_by_email: dict[str, str] = {}
    for email, entries in email_groups.items():
        github_username = email_to_github_username[email]
        if github_username:
            canonical_by_email[email] = github_username
        else:
            display_names = [e[0] for e in entries]
            canonical_by_email[email] = Counter(
                display_names).most_common(1)[0][0]

    display_name_to_emails: dict[str, set[str]] = {}
    for display_name, email in authors:
        if display_name not in display_name_to_emails:
            display_name_to_emails[display_name] = set()
        display_name_to_emails[display_name].add(email)

    canonicals = set(canonical_by_email.values())

    aliases_by_canonical: dict[str, list[str]] = {}
    for display_name, emails in display_name_to_emails.items():
        canonical = None
        for email in emails:
            if email in canonical_by_email:
                potential = canonical_by_email[email]
                if potential in canonicals:
                    canonical = potential
                    break

        if canonical and display_name != canonical:
            if canonical not in aliases_by_canonical:
                aliases_by_canonical[canonical] = []
            if display_name not in aliases_by_canonical[canonical]:
                aliases_by_canonical[canonical].append(display_name)

    for canonical in aliases_by_canonical:
        aliases_by_canonical[canonical] = sorted(
            aliases_by_canonical[canonical])

    return dict(sorted(aliases_by_canonical.items()))


def main():
    aliases = generate_aliases()

    with open(SCRIPT_DIR / "authors_alias.yml", "w", encoding="utf-8") as f:
        yaml.dump(
            aliases, f, allow_unicode=True, default_flow_style=False, sort_keys=False
        )

    print(f"Generated authors_alias.yml with {len(aliases)} canonical authors")


if __name__ == "__main__":
    main()
