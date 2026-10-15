# Contributing to SmartParking

## Getting Started

1. Fork and clone the repo
2. Copy `.env.example` to `.env` and configure
3. Run `make dev` for the development environment
4. Run `make seed` to load demo data

## Branching

Trunk-based development. `main` is protected.

- `feat/<name>` — new features
- `fix/<name>` — bug fixes
- `chore/<name>` — maintenance, deps, CI

## Commit Convention

[Conventional Commits](https://www.conventionalcommits.org/):

```
feat(booking): add block table for double-booking prevention
fix(auth): handle expired refresh tokens gracefully
chore(deps): bump fastapi to 0.115
docs(api): update search endpoint parameters
test(payment): add webhook signature verification tests
```

## Code Style

### Python (backend, ai-service)
- Python 3.12, type hints everywhere
- Ruff for linting and formatting
- mypy for type checking
- Raw MySQL queries with parameterized inputs (`%s`)
- No SQLAlchemy

### JavaScript (frontend)
- React 18, JSX
- ESLint + Prettier
- Tailwind CSS for styling

## Testing

```bash
make test          # Run all tests
make test-backend  # Backend only
make test-ai       # AI service only
make eval-llm      # LLM evaluation harness
```

## Pull Requests

- One feature per PR
- Tests required for booking, payment, and pricing code
- CI must pass
- Request review from at least one maintainer

## Architecture Rules

1. **AI advises, backend decides.** No AI module has transactional authority.
2. **Price is never trusted from the client.** Always server-computed from quotes.
3. **Raw SQL only.** No ORM. Parameterized queries with `%s` placeholders.
4. **Money is integer paise.** Never floating-point for currency.
5. **Timestamps are UTC.** Display in Asia/Kolkata on the frontend.
