#!/usr/bin/env python3

import subprocess
import yaml
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent

EXCLUDE_FILES = {
    "README.md",
    "CONTRIBUTING.md",
    "CONTRIBUTING_CN.md",
    "Preface.md",
    "_Test Article.md",
}


def get_git_authors(file_path: Path) -> tuple[str, list[str]]:
    result = subprocess.run(
        ["git", "log", "--follow", "--format=%an", "--", str(file_path)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    if result.returncode != 0:
        return "", []

    authors = [a.strip() for a in result.stdout.strip().split("\n") if a.strip()]
    if not authors:
        return "", []

    seen = set()
    unique_authors = []
    for author in authors:
        if author not in seen:
            seen.add(author)
            unique_authors.append(author)

    first_author = unique_authors[-1]
    co_authors = [a for a in unique_authors if a != first_author]

    return first_author, co_authors


def get_git_dates(file_path: Path) -> tuple[str, str]:
    result = subprocess.run(
        ["git", "log", "--follow", "--format=%aI", "--", str(file_path)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    if result.returncode != 0:
        return "", ""

    dates = [d.strip() for d in result.stdout.strip().split("\n") if d.strip()]
    if not dates:
        return "", ""

    return dates[-1], dates[0]


def read_frontmatter(file_path: Path) -> tuple[dict, str]:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter_str = parts[1]
            body = parts[2]
            try:
                frontmatter = yaml.safe_load(frontmatter_str) or {}
            except yaml.YAMLError:
                frontmatter = {}
            return frontmatter, body
    return {}, content


def write_frontmatter(file_path: Path, frontmatter: dict, body: str):
    frontmatter_str = yaml.dump(
        frontmatter, allow_unicode=True, default_flow_style=False, sort_keys=False
    )
    new_content = f"---\n{frontmatter_str}---{body}"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)


def find_markdown_files(root: Path) -> list[Path]:
    md_files = []
    for path in root.rglob("*.md"):
        if not path.is_file():
            continue
        if path.name in EXCLUDE_FILES:
            continue
        md_files.append(path)
    md_files.sort()
    return md_files


def main():
    md_files = find_markdown_files(REPO_ROOT)
    processed = 0
    updated = 0

    for file_path in md_files:
        rel_path = file_path.relative_to(REPO_ROOT)

        author, co_authors = get_git_authors(file_path)
        date, lastmod = get_git_dates(file_path)
        if not author:
            print(f"{rel_path}: no git history found")
            continue

        frontmatter, body = read_frontmatter(file_path)

        changes = {}
        if frontmatter.get("author") != author:
            changes["author"] = author
        if frontmatter.get("co-authors") != co_authors:
            changes["co-authors"] = co_authors
        if frontmatter.get("date") != date:
            changes["date"] = date
        if frontmatter.get("lastmod") != lastmod:
            changes["lastmod"] = lastmod

        if changes:
            for key, value in changes.items():
                frontmatter[key] = value
            write_frontmatter(file_path, frontmatter, body)
            print(f"{rel_path}: {changes}")
            updated += 1
        else:
            print(f"{rel_path}: up to date")

        processed += 1

    print(f"\nTotal: {processed} files, {updated} updated")


if __name__ == "__main__":
    main()
