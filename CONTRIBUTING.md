# Submitting an Article

[中文版](CONTRIBUTING_CN.md)

## What is this repository?

This repository securely stores all the article content for the Graduate Texts in Minecraft project. Submissions and revisions of articles are processed here.

## Administration & Roles

This project adopts a flat organizational structure. There are only two roles: reviewers (admins) and writers (users).
Reviewers rotate among the internal writer team. There is no hierarchical difference between an outside contributor and a writer.

Reviewers are responsible for:

- Enforcing writing standards
- Fact checks
- Resolving conflicts on pull requests
- Approving pull requests (PRs)

## Submission Workflow

Submitting an article is straightforward:

1. Submit via the website or GitHub to request a review. You can operate directly on the website, or edit locally and push to GitHub.
2. Fill out the frontmatter (the metadata block) at the top of your markdown file.
3. Write your article using standard Markdown alongside our supported custom syntax (see below).
4. Submit a Pull Request (PR) through the website or GitHub to request a review.

## Frontmatter Guide

Every Markdown file requires a YAML frontmatter block at the very top of the file to track its metadata.

Here is an article metadata example:

```yaml
---
slug: basics-and-structure
title: 前置知识与树场的基本结构
title-en: Basics and Structure
author: YourGitHubName
co-authors:
  - Contributor1
  - Contributor2
date: '2025-02-02T23:57:52+08:00'
lastmod: '2025-07-28T21:48:28+08:00'
index: 1
is-advanced: false
banner:
  src: img/banner.png
  alt: A descriptive alt text
---
```

Field breakdown:

- `title`: The primary title of the article.
- `title-en`: The English translation of the title. (Highly recommended for discoverability)
- `author`: The primary author's GitHub username. *Does not need manual updating.*
- `co-authors`: A YAML array of additional contributors' usernames. *Does not need manual updating.*
- `date`: The original publication or creation date in ISO 8601 format. *Does not need manual updating.*
- `lastmod`: The date of the most recent significant update in ISO 8601 format. *Does not need manual updating.*
- `index`: An integer representing the order of the article in its directory. `-1` means unordered, please do not submit articles with `index: -1`.
- `slug`: The unique URL identifier for the article.
- `is-advanced`: Set to `true` to mark the *entire* article as advanced content.
- `banner`: A nested object containing `src` (relative image path) and `alt` (accessible description of the image).

Here is a chapter/directory (`README.md`) metadata example:

```yaml
---
slug: tree-farm
chapter-title: 树场
chapter-title-en: Tree Farm
intro-title: 前言
intro-title-en: Preface
index: -1
---
```

Field breakdown:

- `chapter-title`: The display name for the chapter/directory.
- `chapter-title-en`: The English translation of the chapter name.
- `intro-title`: The title for the introductory text inside the `README.md`.
- `intro-title-en`: The English translation of the intro title.
- `index`: Ordering integer for the chapter among its siblings.
- `slug`: The unique URL identifier for the chapter directory. In nested chapters, this field can be left empty to omit the URL level.

> [!WARNING]
> The directory structure must not exceed 3 levels of depth.

### Slug Rules

A "slug" is the string used to identify your article or chapter in the final URL. For example, if the chapter slug is `tree-farm` and the article slug is `introduction`, the final URL will be `/tree-farm/introduction`.

Naming Rules:

- Be clear and explicit, reflecting the content of the article. Do not repeat information already included in the chapter slug (e.g., `tree-farm/introduction-to-tree-farms` can be simplified to `tree-farm/introduction`).
- Ensure the uniqueness of the slug to avoid conflicts with other articles or chapters in the same directory.
- Do not use uppercase letters, spaces, underscores, or Chinese characters.
- Do not include chapter or ordering numbers in the slug (e.g., use `title` instead of `01-title`).
- Empty slugs (`slug: ""`) are permitted. If used on a subsection directory, that directory level will be omitted from the final URL entirely (assuming there are no conflicts).

## Custom Markdown Syntax

We provide a few custom Markdown enhancements to make technical writing more expressive and engaging. You can use these special tags directly in your articles (though, of course, they won't render on GitHub).

### Colored Text

When you need to highlight an easy-to-miss warning or distinguish different colored cables, you can use our ANSI color syntax. It's very simple—just wrap your text in brackets with the color name:

```markdown
This is a [red]very important[/red] warning.
You can also use [bright-blue]brighter colors[/bright-blue].
```

**Supported Colors:**

- Standard: `black`, `red`, `green`, `yellow`, `blue`, `magenta`, `cyan`, `white`
- Bright variants: `bright-black` (gray), `bright-red`, `bright-green`, `bright-yellow`, `bright-blue`, `bright-magenta`, `bright-cyan`, `bright-white`

> [!TIP]
> Use colors with restraint—otherwise the page starts to look like a neon sign.

### Advanced Content Sections

Deep technical mechanics can easily overwhelm beginners. If a section contains very hardcore content (such as relatively obscure research or code analysis), just append `[!ADVANCED]` to the end of the heading:

```markdown
## How the RNG Manipulation Works [!ADVANCED]

This section will be marked as advanced content.
```

When rendered, this heading will get a special "Advanced" badge. This keeps the article approachable for beginners while satisfying experts who want to dig deeper.

### Hidden Text

Want to hide an easter egg or the answer to a puzzle without spoiling it immediately? Use the `<hidden>` tag. The text will be blacked out, revealing itself only when the reader hovers over it:

```html
The answer to the puzzle is <hidden>42</hidden>.
```

## Git Standards

We do not strictly require contributors to possess Git knowledge. If you use our [online editor](https://beta.techmc.wiki), Git and Pull Requests are handled entirely as the backend, meaning you won't need to manually deal with commits.

However, if you are editing files locally and pushing to GitHub, you must follow these standards to ensure your PR merges smoothly:

### Clear Commit Messages

Commit messages should be clear and descriptive. A generic message like `Update` is not acceptable.
Whenever applicable, follow the `scope: subject` format.

Example: `entity-ai: add pathfinding walkthrough`.

### Merging

We strongly prefer squash merges to maintain a clean and linear history on the `main` branch.
Rebase merges are only considered occasionally if your branch possesses a very long, valuable, and exceptionally well-structured history.

### No Merge Commits

**Merge commits are strictly prohibited**. Do NOT create any merge commits on your own fork. If your PR includes a merge commit, reviewers will remove it.
