# Proposal

## Why

Grillo needs a small, stable backend foundation before the interview dialogue and ML integration can be developed. The first increment must let a client verify service availability, create and authenticate users, and create and retrieve user-owned interview sessions from persistent storage.

## What Changes

- Introduce a containerized HTTP backend with a public health endpoint.
- Introduce email/password registration and sign-in that issue bearer access tokens.
- Introduce authenticated interview-session creation, listing, and retrieval so a user can return to a named chat.
- Introduce persistent storage with exactly two application tables, `users` and `sessions`, related by `sessions.user_id`.
- Define the initial session setup fields needed for a theory interview: title, target position, and seniority level.
- Keep text-message exchange, AI question generation, answer evaluation, final feedback, frontend, and a standalone ML service outside this initial backend change.

## Capabilities

### New Capabilities

- `service-health`: Public readiness information for the backend and its database dependency.
- `user-authentication`: User registration, credential verification, and access-token issuance.
- `interview-session-management`: Creation and discovery of named, user-owned interview sessions with basic interview configuration.

### Modified Capabilities

None.

## Impact

- Adds the initial backend service and its public HTTP API contract.
- Adds a PostgreSQL schema and migrations for `users` and `sessions`.
- Adds backend and database container definitions for local development.
- Establishes authentication and ownership boundaries that future chat, AI interviewer, and feedback capabilities will build on.
