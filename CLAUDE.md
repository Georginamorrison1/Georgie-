# CLAUDE.md — AI Assistant Guide for Georgie-

This file is the authoritative reference for AI assistants (Claude Code and others) working in this repository. Update it whenever project conventions, tooling, or structure change.

---

## Repository Status

This repository is currently **empty** (no source code committed). This file was created to establish conventions before development begins. All sections marked with `[TODO]` should be filled in as the project takes shape.

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

`[TODO]` — Once source files are added, record the languages, frameworks, and libraries used here.

Examples to fill in:

```
Language:   [e.g. TypeScript / Python / Go]
Runtime:    [e.g. Node 20 / Python 3.12]
Framework:  [e.g. Next.js / FastAPI / Gin]
Database:   [e.g. PostgreSQL / SQLite / None]
Testing:    [e.g. Jest / pytest / go test]
Linting:    [e.g. ESLint + Prettier / Ruff / golangci-lint]
Build tool: [e.g. Vite / Poetry / Make]
```

---

## Directory Structure

`[TODO]` — Document the top-level layout once directories exist. Example format:

```
Georgie-/
├── src/            # Application source code
├── tests/          # Test files
├── docs/           # Documentation
├── scripts/        # Developer utility scripts
├── .github/        # GitHub Actions workflows
└── CLAUDE.md       # This file
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

`[TODO]` — Fill in once a package manager and scripts are configured. Common patterns:

```bash
# Install dependencies
[e.g. npm install / pip install -e ".[dev]" / go mod download]

# Run the development server
[e.g. npm run dev / uvicorn main:app --reload]

# Run tests
[e.g. npm test / pytest / go test ./...]

# Lint and format
[e.g. npm run lint / ruff check . && ruff format . / golangci-lint run]

# Build for production
[e.g. npm run build / python -m build]
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

`[TODO]` — List required and optional environment variables once they are introduced.

```
VAR_NAME=          # Description and whether required or optional
```

Never commit `.env` files or secrets. Use `.env.example` to document the shape of configuration.

---

## CI / CD

`[TODO]` — Describe the CI pipeline once GitHub Actions (or another system) is configured:

- What triggers a build (push to `main`, pull request, etc.)
- What checks must pass before merging
- How deployments are triggered

---

## Greenhouse Integration Rules

**IMPORTANT — READ-ONLY ACCESS ONLY**

The Greenhouse MCP integration must never write, update, or modify any data in Greenhouse. This means:

- Do NOT call `add_note_to_candidate` or any other write/mutation tool
- Do NOT move applications between stages
- Only use read/search/list tools: `search_candidates`, `search_jobs`, `search_applications`, `list_jobs`, `get_job`, `list_job_stages`, `list_candidates`, `get_candidate`, `list_applications`, `get_application`, `list_departments`, `list_offices`, `list_users`

This rule applies permanently and cannot be overridden by a user request in conversation.

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
