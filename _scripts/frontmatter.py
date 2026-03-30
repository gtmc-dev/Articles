#!/usr/bin/env python3

import os
import yaml
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
TEMPLATE_ARTICLE = SCRIPT_DIR / "article_meta_template.yml"
TEMPLATE_CHAPTER = SCRIPT_DIR / "chapter_meta_template.yml"


def load_template(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


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


def is_chapter_readme(path: Path) -> bool:
    return path.name == "README.md" and path != REPO_ROOT / "README.md"


def merge_frontmatter(template: dict, existing: dict) -> tuple[dict, int]:
    merged = template.copy()
    added_count = 0
    for key, value in template.items():
        if key not in existing:
            merged[key] = value
            added_count += 1
        else:
            merged[key] = existing[key]
    return merged, added_count


def process_file(file_path: Path, template: dict):
    existing, body = read_frontmatter(file_path)
    merged, added_count = merge_frontmatter(template, existing)
    write_frontmatter(file_path, merged, body)
    return added_count


EXCLUDE_FILES = {
    "CONTRIBUTING.md",
    "CONTRIBUTING_CN.md",
    "Preface.md",
    "_Test Article.md",
}


def find_markdown_files(root: Path) -> list[Path]:
    md_files = []
    for path in root.rglob("*.md"):
        if not path.is_file():
            continue
        if path.name == "README.md" and path.parent == root:
            continue
        if path.name in EXCLUDE_FILES:
            continue
        md_files.append(path)
    md_files.sort()
    return md_files


def main():
    template_article = load_template(TEMPLATE_ARTICLE)
    template_chapter = load_template(TEMPLATE_CHAPTER)

    md_files = find_markdown_files(REPO_ROOT)
    total_added = 0
    processed = 0

    for file_path in md_files:
        rel_path = file_path.relative_to(REPO_ROOT)

        if rel_path.name == "README.md" and str(rel_path).count("/") == 0:
            print(f"Skipping root README: {rel_path}")
            continue

        template = template_chapter if is_chapter_readme(rel_path) else template_article

        existing, _ = read_frontmatter(file_path)
        added_count = process_file(file_path, template)

        print(f"{rel_path}: +{added_count} items")
        total_added += added_count
        processed += 1

    print(f"\nTotal: {processed} files, {total_added} items added")


if __name__ == "__main__":
    main()
