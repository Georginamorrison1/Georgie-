# CLAUDE.md — AI Assistant Guide for Georgie-

This file is the authoritative reference for AI assistants (Claude Code and others) working in this repository. Update it whenever project conventions, tooling, or structure change.

---

## Repository Status

Initial Airtable integration has been added. Sections marked with `[TODO]` should be filled in as the project grows.

---

## Repository Overview

| Property | Value |
|---|---|
| Repository | `Georginamorrison1/Georgie-` |
| Default branch | `main` (assumed) |
| Remote | `http://local_proxy@127.0.0.1:40246/git/Georginamorrison1/Georgie-` |
| Active dev branch | `claude/claude-md-mluycvytrqh5y5yx-Ojdbw` |

---

## Project Purpose

`[TODO]` — Describe what this project does, who it is for, and the problem it solves.

---

## Tech Stack

```
Language:   Python
Runtime:    Python 3.10+
Framework:  None (standalone scripts)
Database:   Airtable (via pyairtable)
Testing:    [TODO]
Linting:    [TODO]
Build tool: pip / requirements.txt
```

---

## Directory Structure

```
Georgie-/
├── airtable_client.py   # Airtable read/write client
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template (do not commit .env)
└── CLAUDE.md            # This file
```

---

## Development Workflow

### Branching Convention

- Feature branches: `feature/<short-description>`
- Bug fix branches: `fix/<short-description>`
- AI-assisted branches: `claude/<session-id>`
- Do **not** commit directly to `main`

### Commit Messages

Use the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <short summary>

[optional body]
```

Common types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `ci`

Examples:
```
feat(auth): add JWT token validation
fix(api): handle null response from upstream service
docs: update CLAUDE.md with project structure
```

### Pull Requests

- Keep PRs small and focused on a single concern
- Include a description of **what** changed and **why**
- Ensure all checks pass before requesting review
- Link related issues in the PR body

---

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Configure credentials
cp .env.example .env   # then edit .env with your Airtable token and base ID
```

---

## Testing

`[TODO]` — Describe the testing approach once tests exist:

- Where tests live (e.g. `tests/` or co-located with source)
- Unit vs integration vs end-to-end split
- How to run a single test file or test case
- Coverage requirements (if any)

---

## Code Conventions

`[TODO]` — Add project-specific rules as they emerge. General principles to follow until then:

- Prefer clarity over cleverness
- Keep functions small and single-purpose
- Avoid adding code that is unused or speculative
- Do not leave debug logging in committed code
- Delete dead code rather than commenting it out
- Only handle errors at the boundary where they can be meaningfully acted upon

---

## Environment Variables

```
AIRTABLE_API_TOKEN=    # Required. Personal access token from airtable.com/create/tokens
AIRTABLE_BASE_ID=      # Required. Base ID from the Airtable URL (e.g. appXXXXXXXXXXXX)
AIRTABLE_TABLE_NAME=   # Required. Table name or ID within the base
```

Never commit `.env` files or secrets. Use `.env.example` to document the shape of configuration.

---

## CI / CD

`[TODO]` — Describe the CI pipeline once GitHub Actions (or another system) is configured:

- What triggers a build (push to `main`, pull request, etc.)
- What checks must pass before merging
- How deployments are triggered

---

## AI Assistant Guidelines

When working in this repository as an AI assistant:

1. **Read before editing** — Always read the relevant file before modifying it.
2. **Minimal changes** — Only change what is necessary to accomplish the task. Do not refactor unrelated code.
3. **No speculation** — Do not add features, abstractions, or error handling for hypothetical future requirements.
4. **Update this file** — If the project structure, commands, or conventions change, update the relevant section of CLAUDE.md.
5. **Branch discipline** — Develop on the branch specified in the task context. Never push to `main` without explicit permission.
6. **Commit messages** — Follow the Conventional Commits format described above.
7. **Security** — Do not introduce command injection, XSS, SQL injection, or other OWASP Top 10 vulnerabilities. Do not commit secrets.
8. **No emojis** — Unless the user explicitly requests them.

---

## Updating This File

This file should be updated whenever:

- New dependencies or tools are introduced
- The directory structure changes significantly
- New development commands are added or changed
- CI/CD pipelines are configured or modified
- Coding conventions are established or revised

Keep it accurate and concise — an outdated CLAUDE.md is worse than no CLAUDE.md.
