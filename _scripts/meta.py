#!/usr/bin/env python3

import subprocess
import yaml
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
ARTICLES_DIR = REPO_ROOT / "articles"
ALIASES_FILE = SCRIPT_DIR / "authors_alias.yml"
MAINTAINERS_FILE = SCRIPT_DIR / "maintainers.yml"
ARTICLE_TEMPLATE_FILE = SCRIPT_DIR / "article_meta.tmpl.yml"
CHAPTER_TEMPLATE_FILE = SCRIPT_DIR / "chapter_meta.tmpl.yml"

EXCLUDE_FILES = {
    "CONTRIBUTING.md",
    "CONTRIBUTING_CN.md",
    "Preface.md",
    "_Test Article.md",
}

BASE_MANAGED_FIELDS = {"author", "co-authors", "date", "lastmod"}


def load_template(path: Path) -> dict:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def get_template_for_file(
    file_path: Path, article_template: dict, chapter_template: dict
) -> dict:
    if file_path.name == "README.md":
        return chapter_template
    return article_template


def prune_unknown_frontmatter(frontmatter: dict, known_keys: set[str]) -> dict:
    return {k: v for k, v in frontmatter.items() if k in known_keys}


def fill_missing_with_template_defaults(
    frontmatter: dict, template: dict
) -> tuple[dict, dict]:
    merged = dict(frontmatter)
    added_defaults = {}

    for key, default_value in template.items():
        if key not in merged:
            merged[key] = default_value
            added_defaults[key] = default_value

    return merged, added_defaults


def order_frontmatter_by_template(frontmatter: dict, template: dict) -> dict:
    ordered = {}
    for key in template.keys():
        if key in frontmatter:
            ordered[key] = frontmatter[key]

    for key, value in frontmatter.items():
        if key not in ordered:
            ordered[key] = value

    return ordered


def is_frontmatter_ordered_by_template(frontmatter: dict, template: dict) -> bool:
    expected_order = [key for key in template.keys() if key in frontmatter]
    remaining_keys = [key for key in frontmatter.keys() if key not in template]
    return list(frontmatter.keys()) == expected_order + remaining_keys


def load_aliases() -> dict[str, str]:
    if not ALIASES_FILE.exists():
        return {}

    aliases = yaml.safe_load(ALIASES_FILE.read_text(encoding="utf-8")) or {}
    alias_map = {}
    for canonical, alias_list in aliases.items():
        alias_map[canonical] = canonical
        for alias in alias_list:
            alias_map[alias] = canonical
    return alias_map


def load_maintainers() -> list[str]:
    if not MAINTAINERS_FILE.exists():
        return []
    return yaml.safe_load(MAINTAINERS_FILE.read_text(encoding="utf-8")) or []


def resolve_author(author: str, alias_map: dict[str, str]) -> str:
    return alias_map.get(author, author)


def get_git_authors(
    file_path: Path, alias_map: dict[str, str], maintainers: list[str] | None = None
) -> tuple[str, list[str]]:
    result = subprocess.run(
        ["git", "log", "--follow", "--format=%an", "--", str(file_path)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
        encoding="utf-8",
    )

    if result.returncode != 0:
        return "", []

    authors = [a.strip() for a in result.stdout.strip().split("\n") if a.strip()]
    if not authors:
        return "", []

    if maintainers is None:
        maintainers = load_maintainers()

    # First get unique authors by raw name
    seen = set()
    unique_authors = []
    for author in authors:
        if author not in seen:
            seen.add(author)
            unique_authors.append(author)

    # Resolve aliases FIRST, then deduplicate again
    resolved_authors = [resolve_author(a, alias_map) for a in unique_authors]

    # Deduplicate by resolved names to avoid duplicates like "tanhHeng" + "tanh丶桁" -> "tanhHeng" + "tanhHeng"
    seen_resolved = set()
    unique_resolved = []
    for author in resolved_authors:
        if author not in seen_resolved:
            seen_resolved.add(author)
            unique_resolved.append(author)

    # Filter out maintainers - they should not count as article authors
    non_maintainers = [a for a in unique_resolved if a not in maintainers]

    if non_maintainers:
        # Use non-maintainer as author, rest as co-authors
        first_author = non_maintainers[-1]
        co_authors = [a for a in non_maintainers if a != first_author]
    else:
        # Fallback: all commits are from maintainers, use first maintainer as author
        first_author = unique_resolved[-1]
        co_authors = []

    return first_author, co_authors


def get_git_dates(file_path: Path) -> tuple[str, str]:
    maintainers = load_maintainers()
    result = subprocess.run(
        ["git", "log", "--follow", "--format=%aI%x09%an", "--", str(file_path)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
        encoding="utf-8",
    )

    if result.returncode != 0:
        return "", ""

    lines = [l.strip() for l in result.stdout.strip().split("\n") if l.strip()]
    dates = []
    all_dates = []
    for line in lines:
        if "\t" not in line:
            continue
        date, author = line.split("\t", 1)
        all_dates.append(date)
        if author not in maintainers:
            dates.append(date)

    if not dates:
        if all_dates:
            return all_dates[-1], all_dates[0]
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
        frontmatter,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
        indent=2,
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
    alias_map = load_aliases()
    article_template = load_template(ARTICLE_TEMPLATE_FILE)
    chapter_template = load_template(CHAPTER_TEMPLATE_FILE)
    md_files = find_markdown_files(REPO_ROOT)
    processed = 0
    updated = 0

    for file_path in md_files:
        rel_path = file_path.relative_to(REPO_ROOT)

        template = get_template_for_file(file_path, article_template, chapter_template)
        known_frontmatter_keys = set(template.keys())

        frontmatter, body = read_frontmatter(file_path)
        cleaned_frontmatter = prune_unknown_frontmatter(
            frontmatter, known_frontmatter_keys
        )
        merged_frontmatter, added_defaults = fill_missing_with_template_defaults(
            cleaned_frontmatter, template
        )
        ordered_frontmatter = order_frontmatter_by_template(
            merged_frontmatter, template
        )

        changes = {}
        required_git_keys = known_frontmatter_keys & BASE_MANAGED_FIELDS
        computed_values = {}

        if required_git_keys:
            author, co_authors = get_git_authors(file_path, alias_map)
            date, lastmod = get_git_dates(file_path)

            if not author:
                print(f"{rel_path}: no git history found, skipping git-managed fields")
            else:
                computed_values = {
                    "author": author,
                    "co-authors": co_authors,
                    "date": date,
                    "lastmod": lastmod,
                }

        for key in known_frontmatter_keys:
            if (
                key in computed_values
                and merged_frontmatter.get(key) != computed_values[key]
            ):
                changes[key] = computed_values[key]

        if added_defaults:
            changes["added-defaults"] = sorted(added_defaults.keys())

        unknown_keys = set(frontmatter.keys()) - set(cleaned_frontmatter.keys())
        if unknown_keys:
            changes["removed-unknown"] = sorted(unknown_keys)

        if not is_frontmatter_ordered_by_template(merged_frontmatter, template):
            changes["reordered"] = True

        if changes:
            frontmatter = ordered_frontmatter
            for key, value in changes.items():
                if key in {"removed-unknown", "added-defaults", "reordered"}:
                    continue
                frontmatter[key] = value
            frontmatter = order_frontmatter_by_template(frontmatter, template)
            write_frontmatter(file_path, frontmatter, body)
            print(f"{rel_path}: {changes}")
            updated += 1
        else:
            print(f"{rel_path}: up to date")

        processed += 1

    print(f"\nTotal: {processed} files, {updated} updated")


if __name__ == "__main__":
    main()
