---
name: git-commit-governance
description: >
  Enforces enterprise Git workflow with atomic commits, protected main, and PR-first delivery.
  Trigger: when planning commits, creating branches, opening PRs, or defining repo governance.
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
---

## When to Use

- Before creating any commit strategy in this project
- When the user asks for best practices in branches, PRs, or commit granularity
- When preparing release-critical or security-sensitive changes

## Critical Patterns

- Never commit directly to `main`; always use short-lived branches.
- Keep commits atomic: one intent, one semantic change, one clear message.
- Split large work by layer: `chore` scaffold, `feat` domain, `feat` adapters, `test`, `docs`.
- Use Conventional Commits only.
- Require PR checks green before merge.
- Treat potential secret files as blocked by default until sanitized.
- Hard limit by default: target <= 5 files and <= 300 net lines per commit.
- If a change exceeds limits, split before committing; never dump all files in one `git add`.
- Stage explicitly by path groups; verify staged diff before every commit.
- If a commit is too large and still local, rewrite immediately into smaller commits.

## Commit Slicing Guide

| Situation | Commit Strategy | Why |
| --- | --- | --- |
| New module + tests | `feat` then `test` | Isolates behavior from verification |
| Refactor + bugfix | separate `refactor` and `fix` | Clear rollback and blame |
| Docs + code | separate `docs` and code commit | Avoid noisy history |
| Security hardening | dedicated `chore(security)` | Easier auditing |

## Branching Rules

- Branch names:
  - `feat/<scope>-<short-desc>`
  - `fix/<scope>-<short-desc>`
  - `chore/<scope>-<short-desc>`
  - `docs/<scope>-<short-desc>`
- Merge policy:
  - PR required
  - minimum 1 approval
  - no direct pushes to `main`

## Commands

```bash
git checkout -b feat/adapters-contract-hardening
git add app/adapters/openai.py
git commit -m "feat(adapters): add strict response contract validation"
git add tests/test_adapters_contracts.py
git commit -m "test(adapters): cover provider payload drift scenarios"
git push -u origin feat/adapters-contract-hardening
gh pr create --title "feat: harden adapter contracts" --body "..."
```

## Pre-Commit Gate (Mandatory)

Before each commit:

1. `git status --short`
2. `git diff --cached --stat`
3. validate: one concern only, bounded file count/size, no secrets
4. commit with semantic message

If gate fails, split the staged set and retry.

## Resources

- **Governance**: `docs/04-operations/branching-governance.md`
- **Security standard**: `docs/06-security/secrets-operating-standard.md`
