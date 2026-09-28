# Gates: Grillo backend MVP

OWNS: app/**, alembic/**, tests/**, scripts/**, pyproject.toml, uv.lock, .python-version, alembic.ini, Dockerfile, docker-compose.yml, .dockerignore, .env.example, .gitignore, README.md, openspec/changes/bootstrap-grillo-backend-mvp/tasks.md

Scope: containerized FastAPI backend with PostgreSQL persistence, authentication, owned interview sessions, migrations, documentation, and automated verification

- [x] G0: this ledger states executable completion outcomes
  CHECK: node /Users/crysingzz/.agents/skills/unlazy/scripts/gate-lint.mjs GATES.md
  EXPECT: LINT OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=833a518ca6dbd63257074a978626d00010dc64f77adc0593aaa4e9aef1446531; exit=0; EXPECT=matched; output-sha256=48630b7361dd44ee870917b12c3d19b9d7bdea738aaca16bb04d4cab83b772d2; output-bytes=8; shell=/bin/sh; cwd=/Users/crysingzz/Desktop/projects/ai_interview; path=12ea35c619b7/23 entries

- [x] G1: the backend behavior and security contract passes its automated test suite
  CHECK: sh scripts/verify_tests.sh
  EXPECT: backend test suite passed
  EVIDENCE: automatic-evidence=v1; definition-sha256=b6c117f4d93fc9c5ed4ff401fd178552ad8d1041487d42a951acdf8af4ab5f78; exit=0; EXPECT=matched; output-sha256=c96efd5712079bc70750404df43cafb60c63b2646aee95d132ea5f27cf5ea506; output-bytes=839; shell=/bin/sh; cwd=/Users/crysingzz/Desktop/projects/ai_interview; path=12ea35c619b7/23 entries

- [x] G2: the migration creates and rolls back the required PostgreSQL schema
  CHECK: sh scripts/verify_migrations.sh
  EXPECT: migration roundtrip verified
  EVIDENCE: automatic-evidence=v1; definition-sha256=c0b878e1efb82e09e334d9f965190243bc9fb35e4f472d178eaa790d05fd59c2; exit=0; EXPECT=matched; output-sha256=64899a407d3609a154edb6f9e06ebcdfd8e38e1d2c143ae6fc571714fb218c0e; output-bytes=1255; shell=/bin/sh; cwd=/Users/crysingzz/Desktop/projects/ai_interview; path=12ea35c619b7/23 entries

- [x] G3: Docker Compose builds and the containerized API completes the authenticated session smoke flow
  CHECK: sh scripts/verify_backend.sh
  EXPECT: containerized backend verified
  EVIDENCE: automatic-evidence=v1; definition-sha256=a7dc3fe573c3fa83f2d75c78529b65663efa7ab91e5c2a5021d1807465f92447; exit=0; EXPECT=matched; output-sha256=2300154c721133be8e9c1e56e4e99a708bc68f6058034fcc5e371b6ac9a8749d; output-bytes=2857; shell=/bin/sh; cwd=/Users/crysingzz/Desktop/projects/ai_interview; path=12ea35c619b7/23 entries

- [x] G4: project documentation and configuration describe all required routes and runnable commands
  CHECK: uv run --no-sync python scripts/verify_docs.py
  EXPECT: documentation contract verified
  EVIDENCE: automatic-evidence=v1; definition-sha256=c6e40fbc86f89931c53aa8f2a1923eee1f74d13ce771bac8cfa2052b62fc1400; exit=0; EXPECT=matched; output-sha256=a660475546f9ad8a279e01cc2a8a2feab4ebefc5b28523554742e7d37d6ea6fa; output-bytes=32; shell=/bin/sh; cwd=/Users/crysingzz/Desktop/projects/ai_interview; path=12ea35c619b7/23 entries
