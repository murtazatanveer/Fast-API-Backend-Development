# JWT Authentication System Using FastAPI and PostgreSQL

## 1. Project Overview

I want to build a JWT Authentication System using **FastAPI** and **PostgreSQL**.

**Technologies:**

- Backend Framework: FastAPI
- Database: PostgreSQL (hosted on Supabase)

## 2. Architecture Rules: PostgreSQL Configuration

The following rules must be strictly followed when configuring and interacting with PostgreSQL:

- **Database:** PostgreSQL (hosted on Supabase).
- **Driver Mode:** ASYNC ONLY. Use `asyncpg` with `create_async_engine`. Never use synchronous drivers such as `psycopg2` or `create_engine`.
- **Session Management:** Use `async_sessionmaker` with `AsyncSession`. Wrap all route logic in `async with sessionFactory() as db:`.

## 3. Initial Setup and Dependencies

- PostgreSQL has already been configured, and the Supabase connection is working correctly.
- All dependencies mentioned in the `requirements.txt` file have been installed.
- Whenever an additional dependency is required during project development, make sure to add it to `requirements.txt`.

## 4. Project Folder Structure

Follow the folder structure below throughout the project development.

### 1. Configuration

Contains the project's configuration, including environment variables, database connections and sessions, third-party services, and other configurations (e.g., LLM API configuration).

### 2. Routes

Contains the project routes. Each module has a separate route file containing all the endpoints associated with that module.

In this project, we have only one module: `/auth`.

### 3. Controllers

Each route has a separate controller file.

For example, if we have three routes, each with five endpoints, we will have three controller files, with one controller file per route.

### 4. Services

Each route has multiple service files. Each endpoint must have its own service file.

For example, if we have three routes, each with five endpoints, we will have fifteen service files, with five service files per route.

### 5. Dependencies

Contains project-level dependencies, such as middleware and reusable dependencies, including the JWT token verification dependency.

### 6. Schemas

Contains Pydantic models. Each route has a single schema file containing all the Pydantic models required by its endpoints.

### 7. Models

Contains database models, specifically SQLAlchemy ORM models representing the database tables.

### 8. Utils

Contains project-wide helper functions and reusable utilities that are independent of individual routes.

I have already added `responseHelpers.py` to this folder. **All API responses throughout the project must use the response helpers defined in this file.**

## 5. Project Details and JWT Authentication Flow

. Login / Signup
User submits credentials.

Server validates (hash comparison with Argon2id/bcrypt).

Server generates two tokens:

Access token — JWT, 15 min expiry, returned in JSON body.

Refresh token — opaque or JWT, sent as an httpOnly cookie.

Server stores the refresh token hashed in DB with:

sliding_expiry = now + 30 days

absolute_expiry = now + 90 days ← set once, never changes

family_id (for reuse detection)

revoked = false

Cookie set with: httpOnly; Secure; SameSite=Strict/Lax;

Client stores access token in React Context (in-memory, never localStorage).

2. Normal API calls (access token valid)
   Client attaches authToken: Bearer_<access_token>.

Server verifies JWT signature, exp, aud, iss.

Response returned.

3. Access token expires (in-session)
   Server returns 401.

Client 401 interceptor (not a client-side exp check) calls POST /auth/refresh with the cookie.

Server:

Looks up the hashed refresh token in DB.

Checks both sliding_expiry > now and absolute_expiry > now.

If reuse detected (token already rotated/revoked) → revoke entire family → 401.

Otherwise:

Revoke old refresh token row.

Insert new refresh token row:

sliding_expiry = now + 30 days (slides)

absolute_expiry = same as old row (unchanged)

same family_id

Issue new access token.

Client updates Context with new access token, retries the original request.

4. User closes page and reopens later
   Access token in memory is null.

On app mount, client calls POST /auth/refresh once (deduplicated — single in-flight promise).

Server performs the same checks as step 3:

If sliding_expiry expired (inactive > 30 days) → 401 → user logs in again.

If absolute_expiry expired (session > 90 days) → 401 → user logs in again.

Otherwise → rotate token, slide 30 days forward, keep 90-day absolute, return new access token.

User is silently logged in.

5. Logout
   Client calls DELETE /auth/logout.

Server deletes/revokes the refresh token row in DB.

Server clears the cookie.

Client clears Context.

(Client-only clearing is not sufficient — server revocation is required.)

**HTTP methods:** `/auth/refresh` remains `POST` because it rotates state, while `/auth/logout` and `/auth/logout-other-devices` use `DELETE`.

## 6. Endpoint-by-Endpoint Development Approach

The project must be developed **one endpoint at a time**, rather than implementing the entire project at once.

- We will start by developing Endpoint 1, complete and verify its implementation, and then move on to Endpoint 2.
- Each endpoint must be implemented and reviewed individually before proceeding to the next endpoint.
- If any new dependency is required for an endpoint, add it to the `requirements.txt` file and inform the user so they can install it manually.

## 7. Endpoints Architecture Documentation

This file contains a section named **Endpoints Architecture**, which documents the architecture of each endpoint.

This section includes:

- Endpoint description.
- Endpoint execution flow.

Whenever an endpoint's implementation or functionality changes, the corresponding documentation in the **Endpoints Architecture** section must also be updated to reflect those changes.

**Important:** The Endpoints Architecture section must contain only endpoint descriptions and execution flows. Do not include any source code in this section.

## 8. Coding Conventions

- **Folders:** PascalCase (e.g. `Routes`, `Controllers`, `Services`, `Schemas`, `Models`, `Dependencies`, `Utils`, `Configuration`).
- **Python file names:** camelCase (e.g. `authController.py`, `signupService.py`).
- **Class names:** PascalCase (e.g. `User`, `RefreshToken`, `SignupRequest`).
- **Function and method names:** camelCase (e.g. `signupController`, `hashPassword`).
- **Code inside functions and classes:** snake_case for local variables, parameters, instance/module attributes (e.g. `access_token`, `family_id`, `_engine`).
- **Database table names:** PascalCase (e.g. `Users`, `RefreshTokens`).
- **Database column names:** camelCase (e.g. `userId`, `slidingExpiry`), mapped explicitly from snake_case ORM attributes.
- **API JSON keys:** camelCase (e.g. `fullName`, `accessToken`). Pydantic models use snake_case fields with camelCase aliases.
- **`.env` variable names:** UPPER_SNAKE_CASE (e.g. `DB_HOST`, `JWT_SECRET_KEY`).

## Endpoints Architecture

### Endpoint 1 — POST /auth/signup

**Description:**

Registers a new user account. The server validates the submitted username, email, and password, hashes the password with bcrypt, creates the user, and issues an opaque refresh token inside an httpOnly cookie together with a short-lived JWT access token. The refresh token is stored hashed in the database with a 30-day sliding expiry, a fixed 90-day absolute expiry, a new `familyId`, and `revoked = false`. The API responds with a success message and the access token only.

**Request body (JSON, camelCase):**

- `username` — at least 8 characters, must contain at least one uppercase letter, one digit, and one special character.
- `email` — valid email address, unique in the system.
- `password` — at least 8 characters.

**Success response (`201`):**

- `success: true`, `message` (`Account Created Successfully`), `displayUi`, `data.accessToken`.
- No user data is included in the JSON body; the refresh token is never exposed in JSON.
- `Set-Cookie` — `refresh_token`, `HttpOnly`, `Secure`, `SameSite`, 90-day `Max-Age`.

**Execution flow:**

1. Request body is validated (required fields, username rules, email format, password length).
2. Email is normalized (trimmed and lowercased).
3. The service opens an async database session and checks whether the email or username already exists.
4. The password is hashed with bcrypt.
5. A new user row is created with a UUIDv7 identifier.
6. An opaque refresh token is generated; its SHA-256 hash is stored with `familyId`, `slidingExpiry = now + 30 days`, `absoluteExpiry = now + 90 days`, `revoked = false`, and client audit fields.
7. The transaction is committed once; failures are rolled back.
8. The controller returns the success message and access token, sets the refresh cookie, and returns the response.

**Error cases:**

- `409` — email or username already exists.
- `422` — validation failure (invalid email, weak username, short password).
- `500` — unexpected server or database failure.

### Endpoint 2 — POST /auth/login

**Description:**

Authenticates an existing user with a username and password. The server looks up the user by username, verifies the submitted password against the stored bcrypt hash, and issues a new opaque refresh token inside an httpOnly cookie together with a short-lived JWT access token. The refresh token is stored hashed in the database with a new `familyId`, a 30-day sliding expiry, a fixed 90-day absolute expiry, and `revoked = false`. The API responds with a success message and the access token only.

**Request body (JSON, camelCase):**

- `username` — the account username (required).
- `password` — the account password (required).

**Success response (`200`):**

- `success: true`, `message` (`User Login Successfully`), `displayUi`, `data.accessToken`.
- No user data is included in the JSON body; the refresh token is never exposed in JSON.
- `Set-Cookie` — `refresh_token`, `HttpOnly`, `Secure`, `SameSite`, 90-day `Max-Age`.

**Execution flow:**

1. Request body is validated (username and password are required).
2. The service opens an async database session and looks up the user by the trimmed username.
3. The submitted password is verified against the stored bcrypt hash with a constant generic failure message.
4. A new opaque refresh token is generated; its SHA-256 hash is stored with a new `familyId`, `slidingExpiry = now + 30 days`, `absoluteExpiry = now + 90 days`, `revoked = false`, and client audit fields.
5. The transaction is committed once; failures are rolled back.
6. The controller returns the success message and access token, sets the refresh cookie, and returns the response.

**Error cases:**

- `401` — invalid username or password.
- `422` — validation failure (missing username or password).
- `500` — unexpected server or database failure.

### Endpoint 3 — POST /auth/refresh

**Description:**

Rotates the refresh token using the opaque token supplied in the httpOnly cookie. The server hashes the presented token, looks it up in the database, and applies reuse and expiry checks in a strict order. A revoked token is treated as reuse (theft) regardless of its expiry and revokes the entire token family. If the sliding or absolute expiry is hit, every token in the family is deleted. A valid token is revoked and replaced with a new opaque token that keeps the same `familyId` and the same `absoluteExpiry`, while its `slidingExpiry` slides forward by 30 days. The API responds with a success message and a new access token, and sets the rotated refresh token in the cookie.

**Request body:**

- No request body. The refresh token is read from the `refresh_token` httpOnly cookie.

**Success response (`200`):**

- `success: true`, `message` (`Token Refreshed Successfully`), `displayUi`, `data.accessToken`.
- The refresh token is never exposed in JSON.
- `Set-Cookie` — rotated `refresh_token`, `HttpOnly`, `Secure`, `SameSite`, 90-day `Max-Age`.

**Execution flow:**

1. The refresh token is read from the `refresh_token` cookie; if it is missing or blank, the request fails.
2. The presented token is hashed with SHA-256 and looked up by `tokenHash` using a row lock (`SELECT ... FOR UPDATE`) to serialize concurrent refreshes.
3. If no row is found, the request fails.
4. If the row is `revoked` (reuse detected), every non-revoked token in its `familyId` is revoked and the request fails. This check takes precedence over all expiry checks, so a revoked token that is also expired is still treated as reuse.
5. If the row's `absoluteExpiry` is not after the current time (session older than 90 days), every token in its `familyId` is deleted and the request fails.
6. If the row's `slidingExpiry` is not after the current time (inactive for more than 30 days), every token in its `familyId` is deleted and the request fails.
7. Otherwise, the presented row is revoked and a new opaque refresh token is created with the same `familyId`, the same `absoluteExpiry`, `slidingExpiry = now + 30 days`, `revoked = false`, and the current request's client audit fields; the transaction is committed.
8. A new access token is issued for the row's `userId`; the controller returns the success message and access token, sets the rotated refresh cookie, and returns the response.

**Error cases:**

- `401` — missing or unknown refresh token, reuse detected, sliding expiry exceeded, or absolute expiry exceeded; the message is always `Session expired. Please log in again.` and the refresh cookie is cleared.
- `500` — unexpected server or database failure (the refresh cookie is left unchanged).

### Endpoint 4 — DELETE /auth/logout

**Description:**

Ends the current refresh-token session. The endpoint is protected by a reusable JWT dependency that validates the access token supplied in the `authToken: Bearer_<accessToken>` header. It reads the opaque refresh token from the httpOnly cookie, hashes it, and looks it up in the database. If the token is found and belongs to the authenticated user, every token with the same `familyId` is deleted. Logout is idempotent: a missing, unknown, or already-deleted refresh token still succeeds, and the cookie is always cleared on success. The access token itself remains valid until its own expiry because access tokens are stateless.

**Request:**

- `authToken` header — `Bearer_<accessToken>` (required; validated by the shared JWT dependency).
- `refresh_token` httpOnly cookie (optional for idempotency).
- No request body.

**Success response (`200`):**

- `success: true`, `message` (`User Logged Out Successfully`), `displayUi`.
- No `data` is returned and the refresh token is never exposed in JSON.
- `Set-Cookie` — `refresh_token` cleared (empty value, `Max-Age=0`, `HttpOnly`, `Secure`, `SameSite`).

**Execution flow:**

1. The JWT dependency reads the required `authToken` header, requires the `Bearer_` prefix, strips it, and decodes the token, verifying its signature, `exp`, `aud`, and `iss`. It also requires `type = access` and a valid UUID `sub`; otherwise the request fails with `401` before the controller runs. A missing `authToken` header fails with `422`.
2. The refresh token is read from the `refresh_token` cookie; if it is missing or blank, the request succeeds and the cookie is cleared.
3. The presented token is hashed with SHA-256 and looked up by `tokenHash` using a row lock (`SELECT ... FOR UPDATE`) to serialize with concurrent refreshes.
4. If no row is found, the request succeeds and the cookie is cleared.
5. If the row's `userId` does not match the authenticated user, no tokens are deleted and the request still succeeds with the cookie cleared.
6. Otherwise, every token with the row's `familyId` is deleted and the transaction is committed; other sessions/families remain active.
7. The controller clears the refresh cookie and returns the success message.

**Error cases:**

- `422` — the `authToken` header is missing.
- `401` — the `authToken` value has no `Bearer_` prefix, contains no token, or the token is malformed, expired, or otherwise invalid, or is not an access token; the message is `Unauthorized` and the refresh cookie is not cleared.
- `500` — unexpected server or database failure (the refresh cookie is left unchanged).

### Endpoint 5 — DELETE /auth/logout-other-devices

**Description:**

Ends every refresh-token session for the authenticated user except the current device. The endpoint is protected by the shared JWT dependency. It reads the authenticated user ID from the access token, reads the opaque refresh token from the httpOnly cookie, and uses its `familyId` to identify the current device. After confirming the refresh token belongs to the authenticated user, every token row for that user with a different `familyId` is deleted (including revoked history rows). The current device's family is left untouched, and the cookie is neither cleared nor rotated, so this device stays logged in. The success message reports how many other active devices were logged out.

**Request:**

- `authToken` header — `Bearer_<accessToken>` (required; validated by the shared JWT dependency).
- `refresh_token` httpOnly cookie (required; identifies the current device's `familyId`).
- No request body.

**Success response (`200`):**

- `success: true`, `displayUi`.
- `message` — `No other devices to log out` when zero other active devices were deleted; `Logged out from 1 device` for one; `Logged out from N devices` otherwise.
- No `data` is returned and the refresh token is never exposed in JSON.
- No `Set-Cookie` is sent; the current cookie is left unchanged.

**Execution flow:**

1. The JWT dependency reads the required `authToken` header, requires the `Bearer_` prefix, strips it, and decodes the token, verifying its signature, `exp`, `aud`, and `iss`. It also requires `type = access` and a valid UUID `sub`; otherwise the request fails with `401` before the controller runs. A missing `authToken` header fails with `422`.
2. The authenticated user ID is taken from the access token's `sub`.
3. The refresh token is read from the `refresh_token` cookie; if it is missing or blank, the request fails with `401`.
4. The presented token is hashed with SHA-256 and looked up by `tokenHash` using a row lock (`SELECT ... FOR UPDATE`) to find the current device's `familyId`. Revoked or expired current tokens are still accepted for identifying the device.
5. If no row is found or its `userId` does not match the authenticated user, the request fails with `401`.
6. The number of other active devices is counted as the distinct `familyId` values for the user, excluding the current family, that have at least one non-revoked row.
7. Every row for the user whose `familyId` differs from the current family is deleted; the current family is untouched.
8. The transaction is committed and the controller returns `200` with the count-based message; the refresh cookie is not modified.

**Error cases:**

- `422` — the `authToken` header is missing.
- `401` — the `authToken` value has no `Bearer_` prefix, contains no token, or the token is malformed, expired, or otherwise invalid, or is not an access token; or the refresh cookie is missing, blank, unknown, or belongs to a different user. The message is `Unauthorized` and no cookie is cleared.
- `500` — unexpected server or database failure (the refresh cookie is left unchanged).
