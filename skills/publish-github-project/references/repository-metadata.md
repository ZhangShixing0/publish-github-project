# GitHub repository metadata

GitHub repository cards show metadata that is separate from the repository README. A polished README alone does not populate the description or Topics shown in search and profile lists.

## Required metadata decision

Before a new repository is created, derive or ask for:

- **Description**: one concrete sentence, normally 60–140 characters, stating what the project is and who it helps. Do not repeat the repository name or claim an unverified production status.
- **Topics**: 3–10 lowercase, short, truthful terms describing the domain, primary technologies, and maturity. Use GitHub topic syntax: letters, numbers, and hyphens; avoid private names, customer names, or speculative integrations.
- **Homepage**: only when there is a stable public demo, documentation site, or product page. Do not use `localhost`, a temporary preview, or a private internal URL.
- **Visibility**: private by default for new repositories unless the user explicitly chooses public.
- **Default branch**: normally `main`; verify after creation.

For an existing repository, preserve current metadata unless the user explicitly asks to revise it. A user asking to publish a newly created repository has authorized setting the confirmed metadata as part of that publish operation; public visibility, repository deletion, archiving, and collaborator changes still require explicit authority.

## Commands

Using GitHub CLI, after the repository exists:

```shell
gh repo edit OWNER/REPO \
  --description "Concrete project description"
gh repo edit OWNER/REPO --add-topic topic-one --add-topic topic-two
gh repo edit OWNER/REPO --homepage https://example.com
```

Set a new repository's decided visibility when creating it. Do not bundle a visibility change into routine metadata edits on an existing repository. On Windows shells, keep each command as a single invocation or use the tool's structured arguments; do not expose tokens in command text. If no homepage exists, omit the flag. If a topic is rejected, report it and continue with the remaining approved topics rather than silently replacing it.

## Verification

After push, verify through GitHub API or `gh repo view`:

```shell
gh repo view OWNER/REPO --json name,isPrivate,defaultBranchRef,description,homepageUrl,repositoryTopics,url
```

The final report should include the repository URL, visibility, default branch, description, topics, and remote commit SHA. If remote Git transport is unavailable but the GitHub API responds, use the API as evidence and state the transport limitation.
