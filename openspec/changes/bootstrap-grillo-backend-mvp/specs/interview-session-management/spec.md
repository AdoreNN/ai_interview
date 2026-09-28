# Spec Delta

## Purpose

Lets an authenticated user create and rediscover named theory-interview sessions while keeping every session isolated to its owner.

## ADDED Requirements

### Requirement: User can create a configured interview session
The system SHALL expose `POST /api/v1/sessions` to authenticated users and accept a title, target position, and experience level. The title and target position SHALL be non-empty after trimming, the title SHALL contain at most 120 characters, and the experience level SHALL be one of `intern`, `junior`, `middle`, or `senior`.

#### Scenario: Session creation succeeds
- **WHEN** an authenticated user submits a valid title, target position, and experience level
- **THEN** the system creates a session owned by that user and returns HTTP 201 with its identifier, configuration, `created` status, and timestamps

#### Scenario: Session configuration is invalid
- **WHEN** an authenticated user submits an empty or overlong title, an empty target position, or an unsupported experience level
- **THEN** the system returns HTTP 422 and does not create a session

### Requirement: User can list their sessions
The system SHALL expose `GET /api/v1/sessions` to authenticated users and return only sessions owned by the current user, ordered from most recently updated to least recently updated. Each item SHALL include the session identifier, title, target position, experience level, status, and timestamps.

#### Scenario: User has sessions
- **WHEN** an authenticated user requests their session list
- **THEN** the system returns HTTP 200 with that user's session summaries in descending update order

#### Scenario: User has no sessions
- **WHEN** an authenticated user with no sessions requests their session list
- **THEN** the system returns HTTP 200 with an empty list

### Requirement: User can retrieve one owned session
The system SHALL expose `GET /api/v1/sessions/{session_id}` to authenticated users and return the stored details only when the requested session belongs to the current user.

#### Scenario: Owned session is retrieved
- **WHEN** an authenticated user requests a session they own
- **THEN** the system returns HTTP 200 with the session identifier, title, target position, experience level, status, and timestamps

#### Scenario: Session does not exist or belongs to another user
- **WHEN** an authenticated user requests an unknown session identifier or a session owned by another user
- **THEN** the system returns HTTP 404 without revealing whether another user's session exists

### Requirement: Sessions are persistently associated with their owner
The system SHALL persist users and sessions in two application tables and SHALL associate each session with exactly one user through a required `user_id` relationship.

#### Scenario: Session owner is stored
- **WHEN** a session is created successfully
- **THEN** its persisted record references the authenticated user's persisted record through `user_id`

#### Scenario: Orphan session is rejected
- **WHEN** persistence is attempted with a `user_id` that does not reference an existing user
- **THEN** the database rejects the session record

