# Gates: integrated Grillo application

OWNS: app/**, pdf_parser_agent/**, alembic/**, tests/**, scripts/**, pyproject.toml, uv.lock, Dockerfile, docker-compose.yml, .dockerignore, .env.example, .gitignore, README.md, GATES.md

Scope: combine the backend, interview agents, and resume parser into one secure, documented, containerized application on develop

- [ ] G0: this ledger states executable completion outcomes
  CHECK: node /Users/crysingzz/.agents/skills/unlazy/scripts/gate-lint.mjs GATES.md
  EXPECT: LINT OK
  EVIDENCE: pending

- [ ] G1: the merged source excludes secrets, virtual environments, caches, and generated binaries
  CHECK: uv run --no-sync python scripts/verify_source_hygiene.py
  EXPECT: source hygiene verified
  EVIDENCE: pending

- [ ] G2: backend, resume parsing, interview flow, persistence, ownership, and failure behavior pass the automated test suite
  CHECK: sh scripts/verify_tests.sh
  EXPECT: integrated test suite passed
  EVIDENCE: pending

- [ ] G3: database migrations upgrade and downgrade the integrated schema cleanly
  CHECK: sh scripts/verify_migrations.sh
  EXPECT: migration roundtrip verified
  EVIDENCE: pending

- [ ] G4: Docker Compose builds and the integrated services pass the authenticated end-to-end smoke flow
  CHECK: sh scripts/verify_stack.sh
  EXPECT: integrated stack verified
  EVIDENCE: pending

- [ ] G5: documentation and generated configuration describe every required service, route, and environment variable
  CHECK: uv run --no-sync python scripts/verify_docs.py
  EXPECT: documentation contract verified
  EVIDENCE: pending
