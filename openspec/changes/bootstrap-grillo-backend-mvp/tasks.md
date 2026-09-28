# Tasks

## 1. Backend Foundation

- [x] 1.1 Create the Python 3.12 FastAPI project structure with pinned runtime and test dependencies, and verify a clean dependency installation succeeds.
- [x] 1.2 Add typed environment configuration for database URL, JWT signing secret, access-token lifetime, and allowed origins, and verify tests reject missing required production settings.
- [x] 1.3 Add the application factory, `/api/v1` router composition, and consistent error responses, and verify the generated OpenAPI document contains the planned route groups.

## 2. Persistence and Migrations

- [x] 2.1 Configure SQLAlchemy 2 database sessions and Alembic metadata, and verify an application database connection can execute a trivial query.
- [x] 2.2 Implement the `users` and `sessions` models with UUID keys, normalized unique email, password hash, timestamps, required indexed `sessions.user_id`, interview configuration, and constrained status/level values; verify model-level persistence tests pass.
- [x] 2.3 Create the initial Alembic migration with exactly the two domain tables and their foreign-key, uniqueness, index, and check constraints, and verify upgrade from an empty database plus downgrade completes successfully.

## 3. Health Capability

- [x] 3.1 Implement public `GET /health` with a database readiness check, and verify API tests cover HTTP 200 `ok` and HTTP 503 `unavailable` responses.

## 4. Authentication Capability

- [x] 4.1 Implement email normalization and Argon2 password hashing/verification utilities, and verify unit tests cover case normalization, successful verification, and incorrect passwords.
- [x] 4.2 Implement short-lived signed JWT creation and bearer-token validation with the user UUID as subject, and verify tests cover valid, malformed, expired, and unknown-user tokens.
- [x] 4.3 Implement `POST /api/v1/auth/sign-up` with validation, safe persistence, and duplicate-email conflict handling, and verify API tests cover 201, 409, and 422 scenarios without exposing password hashes.
- [x] 4.4 Implement `POST /api/v1/auth/sign-in` with generic credential failures, and verify API tests cover successful token issuance plus unknown-email and wrong-password HTTP 401 responses.
- [x] 4.5 Add the shared current-user authentication dependency, and verify protected-route tests reject missing, invalid, and expired bearer tokens with HTTP 401.

## 5. Interview Session Capability

- [x] 5.1 Implement session request/response schemas and creation service for title, target position, and experience level, and verify validation tests cover trimming, title length, empty values, and allowed levels.
- [x] 5.2 Implement authenticated `POST /api/v1/sessions`, and verify the API creates a `created` session linked to the token's user and returns HTTP 201.
- [x] 5.3 Implement authenticated `GET /api/v1/sessions` ordered by latest update, and verify API tests return an empty list or only the current user's summaries in the specified order.
- [x] 5.4 Implement authenticated `GET /api/v1/sessions/{session_id}` using an owner-scoped query, and verify API tests return owned data while unknown and foreign-owned identifiers both return HTTP 404.

## 6. Containers and Delivery Verification

- [x] 6.1 Add a production-oriented backend Dockerfile, `.dockerignore`, example environment file, and Compose services for backend and PostgreSQL 16 with a named volume and health checks; verify both images/services build successfully.
- [x] 6.2 Wire migration execution and API startup into the local container workflow, and verify a clean Compose startup reaches a healthy database, applies the migration, and serves HTTP 200 from `/health`.
- [x] 6.3 Document local setup, environment variables, migration commands, test commands, and the six API routes in README, and verify a new checkout can follow the documented commands without undocumented manual steps.
- [x] 6.4 Run the complete test suite and an end-to-end smoke flow (sign-up, sign-in, create session, list sessions, retrieve session), and verify all commands pass against the containerized PostgreSQL service.
