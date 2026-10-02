# Spec Delta

## Purpose

Allows Grillo users to create an account and authenticate securely so protected interview data can be associated with a verified identity.

## ADDED Requirements

### Requirement: User can register with email and password
The system SHALL expose `POST /api/v1/auth/sign-up`, accept a valid email address and a password of at least 8 characters, store the email in a case-insensitive form, and store only a one-way password hash.

#### Scenario: Registration succeeds
- **WHEN** a client submits a valid email and password that are not already registered
- **THEN** the system creates the user and returns HTTP 201 with the user's public identifier, email, bearer access token, and token type

#### Scenario: Email is already registered
- **WHEN** a client submits an email that matches an existing account regardless of letter case
- **THEN** the system returns HTTP 409 and does not create another user

#### Scenario: Registration input is invalid
- **WHEN** a client submits an invalid email or a password shorter than 8 characters
- **THEN** the system returns HTTP 422 and does not create a user

### Requirement: User can sign in
The system SHALL expose `POST /api/v1/auth/sign-in` and issue a time-limited bearer access token when supplied credentials match a registered account.

#### Scenario: Sign-in succeeds
- **WHEN** a client submits the email and password of a registered user
- **THEN** the system returns HTTP 200 with the user's public identifier, email, bearer access token, and token type

#### Scenario: Sign-in credentials are invalid
- **WHEN** a client submits an unknown email or incorrect password
- **THEN** the system returns HTTP 401 with the same generic authentication error for either case

### Requirement: Protected endpoints require a valid access token
The system SHALL authenticate protected requests from the bearer token and SHALL derive the current user identity from the token rather than accepting a user identifier from the client.

#### Scenario: Valid token is supplied
- **WHEN** a client calls a protected endpoint with a valid, unexpired bearer access token
- **THEN** the system processes the request as the token's user

#### Scenario: Token is missing or unusable
- **WHEN** a client calls a protected endpoint without a bearer token or with an invalid or expired token
- **THEN** the system returns HTTP 401 without exposing protected data

