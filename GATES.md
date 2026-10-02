# Gates: integrated Grillo application

OWNS: app/**, pdf_parser_agent/**, frontend/**, alembic/**, tests/**, scripts/**, pyproject.toml, uv.lock, Dockerfile, docker-compose.yml, .dockerignore, .env.example, .gitignore, README.md, GATES.md

Scope: combine the backend, interview agents, resume parser, and a production-ready conversational UI into one secure, documented, containerized application on develop

- [x] G0: this ledger states executable completion outcomes
  CHECK: node /Users/crysingzz/.agents/skills/unlazy/scripts/gate-lint.mjs GATES.md
  EXPECT: LINT OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=833a518ca6dbd63257074a978626d00010dc64f77adc0593aaa4e9aef1446531; exit=0; EXPECT=matched; output-sha256=48630b7361dd44ee870917b12c3d19b9d7bdea738aaca16bb04d4cab83b772d2; output-bytes=8; shell=/bin/sh; cwd=/Users/crysingzz/Desktop/projects/ai_interview; path=4c54403d9341/28 entries

- [x] G1: the merged source excludes secrets, virtual environments, caches, and generated binaries
  CHECK: uv run --no-sync python scripts/verify_source_hygiene.py
  EXPECT: source hygiene verified
  EVIDENCE: automatic-evidence=v1; definition-sha256=dd906073cc09a4b825e29adc8bbbdd13a270cf90d47fd6f781e47e3c50039183; exit=0; EXPECT=matched; output-sha256=259db8bd05d8c7a9268142eb24dbf3c06668d0d8a51016cc3a921e8d4541ab03; output-bytes=24; shell=/bin/sh; cwd=/Users/crysingzz/Desktop/projects/ai_interview; path=4c54403d9341/28 entries

- [x] G2: backend, resume parsing, interview flow, persistence, ownership, and failure behavior pass the automated test suite
  CHECK: sh scripts/verify_tests.sh
  EXPECT: integrated test suite passed
  EVIDENCE: automatic-evidence=v1; definition-sha256=aa5bea674c6b813d9a1c15aa436a650581d6387ae6092960325042256096d6b6; exit=0; EXPECT=matched; output-sha256=e4844e03fd522483023940eb05b7a08bcfdcd4b3432af4fe2318cc0abedc9a19; output-bytes=900; shell=/bin/sh; cwd=/Users/crysingzz/Desktop/projects/ai_interview; path=4c54403d9341/28 entries

- [x] G3: database migrations upgrade and downgrade the integrated schema cleanly
  CHECK: sh scripts/verify_migrations.sh
  EXPECT: migration roundtrip verified
  EVIDENCE: automatic-evidence=v1; definition-sha256=c0b878e1efb82e09e334d9f965190243bc9fb35e4f472d178eaa790d05fd59c2; exit=0; EXPECT=matched; output-sha256=ee87871198d9bc6fbac7fef5ff1cd920bddd81a237d0170fb8341efb2a2975cc; output-bytes=996; shell=/bin/sh; cwd=/Users/crysingzz/Desktop/projects/ai_interview; path=4c54403d9341/28 entries

- [x] G4: Docker Compose builds and the integrated services pass the authenticated end-to-end smoke flow
  CHECK: sh scripts/verify_stack.sh
  EXPECT: integrated stack verified
  EVIDENCE: automatic-evidence=v1; definition-sha256=e0da2679c769f9bd4068938f28af408a66c91c0da030d4c4b7916423bcd31829; exit=0; EXPECT=matched; output-sha256=8445450ef3ec868bacb042548707a49ad04199b1227be6bd5d2102995bc23844; output-bytes=4950; shell=/bin/sh; cwd=/Users/crysingzz/Desktop/projects/ai_interview; path=4c54403d9341/28 entries

- [x] G5: documentation and generated configuration describe every required service, route, and environment variable
  CHECK: uv run --no-sync python scripts/verify_docs.py
  EXPECT: documentation contract verified
  EVIDENCE: automatic-evidence=v1; definition-sha256=c6e40fbc86f89931c53aa8f2a1923eee1f74d13ce771bac8cfa2052b62fc1400; exit=0; EXPECT=matched; output-sha256=a660475546f9ad8a279e01cc2a8a2feab4ebefc5b28523554742e7d37d6ea6fa; output-bytes=32; shell=/bin/sh; cwd=/Users/crysingzz/Desktop/projects/ai_interview; path=4c54403d9341/28 entries

- [x] G6: the responsive frontend compiles into a production bundle
  CHECK: npm run build
  EXPECT: built in
  CWD: frontend
  EVIDENCE: automatic-evidence=v1; definition-sha256=2cd968a1268d16cbbd7130efee5cda372ac20f4ab5d2df9f2067149f8c58c3a7; exit=0; EXPECT=matched; output-sha256=4b5570c1af62f99351283b71ba22aafe27f4ed93ef5f48da92fb7eebb34a3017; output-bytes=402; shell=/bin/sh; cwd=/Users/crysingzz/Desktop/projects/ai_interview/frontend; path=4c54403d9341/28 entries

- [x] G7: the UI exposes the complete auth, session, resume, and interview workflow through the backend API contract
  CHECK: npm run verify
  EXPECT: UI contract verified
  CWD: frontend
  EVIDENCE: automatic-evidence=v1; definition-sha256=41753c85d29d040d761b0af8a968b503cbc636302f34c42beba7a5397c9700b1; exit=0; EXPECT=matched; output-sha256=080896b69c831e8fae83473c44780b271567cb38696c78691155ea43dc969203; output-bytes=83; shell=/bin/sh; cwd=/Users/crysingzz/Desktop/projects/ai_interview/frontend; path=4c54403d9341/28 entries

- [x] G8: Docker Compose includes the frontend and resolves the complete four-service application configuration
  CHECK: sh scripts/verify_frontend_stack.sh
  EXPECT: frontend stack configuration verified
  EVIDENCE: automatic-evidence=v1; definition-sha256=a9e1917e5918793930a527ecc10a18fc28999d22d1efdd719fd2c3ef235df95e; exit=0; EXPECT=matched; output-sha256=23b78ca8915da5a52b723bceabb02f014a5f8db2ed5558be821851e0790d4cfa; output-bytes=38; shell=/bin/sh; cwd=/Users/crysingzz/Desktop/projects/ai_interview; path=4c54403d9341/28 entries

- [x] G9: the desktop and mobile layouts visually combine cobalt's compact dark utility style with ChatGPT's conversational hierarchy
  EVIDENCE: reviewed rendered 1440x960 auth, interview, and setup screens plus 390x844 setup, overlay navigation, and interview screens; confirmed readable hierarchy, responsive composer, keyboard focus states, and overflow behavior
