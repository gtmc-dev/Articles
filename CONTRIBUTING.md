# Submitting an Article

[中文版](CONTRIBUTING_CN.md)

## Structure of Administration

This project adopts a flat organizational structure. The only two roles are reviewers (admins) and writers (users). Reviewers are rotating among the internal writer team. Other from that, there are no differences between an outside contributor and a writer.

## Rotating Reviewers

Reviewers will be rotating among the writer team.

Reviewers are responsible for:

- Enforcing writing standards
- Fact checks
- Resolving conflicts on merge requests
- Approving merge requests

## Contributing

Simply clone this repo, stay updated by pulling the latest changes, and submit a merge request with your article. The reviewers will review your article and merge it if:

- It meets our quality standards
- All conflicts are resolved

## About Article Slugs

A slug is the identifier displayed in the URL of an article. For example, the file path `TreeFarm/01-前置知识与树场的基本结构.md` corresponds to the URL `techmc.wiki/articles/tree-farm/basics`. This is defined by the `slug` field in the Front Matter at the top of each article. Please ensure that each article has a unique and descriptive slug so readers can easily understand the content from the URL.

Reviewers will also check the correctness of slugs when reviewing merge requests.

### How to Add a Slug

If you are using the web editor, there will be an input box at the top of the page for you to enter the slug. Please read the following specifications to ensure your slug meets the requirements.

If you are editing in a local editor, add YAML frontmatter at the top of your Markdown file:

```markdown
---
slug: "your-slug-here"
---

# Article Title

Content...
```

### Slug Requirements

A slug must follow these rules:

- Only lowercase letters (a–z), numbers (0–9), and hyphens (`-`) are allowed.
- Uppercase letters, underscores, spaces, special characters, Chinese characters, or any other characters are not allowed.
- Do not include chapter numbers in the slug. For example, `01-title` is not appropriate; use `title` instead.

### Slugs for Sections / Directories

Each top-level directory must contain a `README.md` file, and the slug for that directory should be defined within it using the same format as above.

Note: The repository must not exceed three levels of directory depth.

### Omitting Subsection Slugs

It is allowed to omit subsection slugs (i.e., explicitly set `slug: ""`). If a subsection slug is empty and there is no conflict at the same level, that level may be omitted in the URL.

For example, if the slug in `Twisuki/README.md` is empty, then the URL for `Twisuki/01-article.md` will be `/articles/article` instead of `/articles/twisuki/article`.

## Git Standards

We don't want to require any `git` knowledge for contributors. However, to preserve traceability and transparency of the editting history, we still have to enforce some standards on commits.

If you are not familiar with `git`, don't worry. Our [online editor](https://beta.techmc.wiki) uses Git and Pull Requests as the backend, but most technical details will be hidden from contributors, so most standards can be satisfied effortlessly by simply following the instructions on the website. If you know git and write on your local editor, you might want to read the standards below to make sure your PR can be merged smoothly.

Reviewers should also read these standards and enforce them when reviewing PRs.

### Clear commit title and description

Commit messages should be clear and descriptive. Something like `Update` is not acceptable. A good commit message should be concise yet descriptive enough to understand your changes without looking at the diff.

If applicable, you should follow the `scope: subject` format, e.g. `entity ai: add code walkthrough for the pathfinding algorithm`. Try not to exceed 72 characters for the title, you may cramble the rest of the description in the body if necessary.

### Merging

For a strict linear history on main, all branches should be merged through squash merges, or only very occasionally, rebase merges. A rebase merge might be used for the following scenarios:

- Your branch has a very long and valuable history that we don't want to lose by squashing.
- Most commits in your branch are already well-structured and meaningful.
- Your branch contains a lots of edits that cannot be easily crambled into a single commit.

Merge commits are strictly prohibited. Do NOT create any of them on your own fork. See [Preventing Merge Commits](NO_MERGE_COMMITS.md) for more instructions on how to avoid creating merge commits. We will revise pull requests to remove merge commits if they contain any.
