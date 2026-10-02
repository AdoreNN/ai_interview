# Spec Delta

## Purpose

Provides a public probe that reports whether the Grillo backend and its required database dependency are ready to serve requests.

## ADDED Requirements

### Requirement: Service health can be checked without authentication
The system SHALL expose `GET /health` without requiring an access token.

#### Scenario: Backend and database are available
- **WHEN** a client requests `GET /health` and the backend can reach the database
- **THEN** the system returns HTTP 200 with a machine-readable status of `ok`

#### Scenario: Database is unavailable
- **WHEN** a client requests `GET /health` and the backend cannot reach the database
- **THEN** the system returns HTTP 503 with a machine-readable status of `unavailable`

