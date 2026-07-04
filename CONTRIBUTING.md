# Contributing — Team Norms
 
Two-person project. These rules exist so we never block each other and never surprise each other during build.
 
## Ownership
 
- `engine/` — Zineb. `app/` — Nitesh. `tests/` and `CONTRACT.md` — shared.
- Don't edit the other person's directory without a heads-up.

## Branches & PRs
 
- `main` is protected. Nothing enters it without a reviewed PR (pull request). 
- One branch per task, named after the Issue it solves: `feature/sql-validation`, `fix/upload-encoding`.
- Pull `main` into your branch at the start of every session.
- Keep PRs small — one Issue per PR, reviewable in ~10 minutes.
- Every PR description says: what it does, how it was tested, `Closes #N`.
- The **other** person reviews before merge. 

## Commits
 
Commit after every meaningful step, never everything at once. Conventional commits:
 
- `feat:` new functionality
- `fix:` bug fix
- `chore:` setup, config, dependencies, refactor
- `docs:` README, contract, documentation
- `test:` adding or fixing tests
- `style:` formatting only

## Secrets
 
- Never commit `.env`. Ever.
- Every new environment variable gets added to `.env.example` in the same PR that introduces it.

## Contract discipline
 
- `CONTRACT.md` changes require agreement from both and a PR.
- Python managed with uv - run uv sync after pulling.

## Definition of done (v1)
 
- [ ] End-to-end flow works: upload → question → validated SQL → answer + chart
- [ ] Guardrails proven by tests (destructive SQL blocked, timeout works)
- [ ] Eval results table filled in the README, both providers
- [ ] Deployed demo live (OpenAI mode) + local instructions verified on a clean machine
- [ ] README complete, including Honest Notes
- [ ] Every line in `main` arrived through a reviewed PR