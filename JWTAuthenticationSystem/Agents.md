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
   Client attaches Authorization: Bearer\_<access_token>.

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
   Client calls POST /auth/logout.

Server deletes/revokes the refresh token row in DB.

Server clears the cookie.

Client clears Context.

(Client-only clearing is not sufficient — server revocation is required.)

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

Registers a new user account. The server validates the submitted username, email, and password, hashes the password with bcrypt, creates the user, issues a 15-minute JWT access token in the JSON body, and issues an opaque refresh token inside an httpOnly cookie. The refresh token is stored hashed in the database with a 30-day sliding expiry, a fixed 90-day absolute expiry, a new `familyId`, and `revoked = false`.

**Request body (JSON, camelCase):**

- `username` — at least 8 characters, must contain at least one uppercase letter, one digit, and one special character.
- `email` — valid email address, unique in the system.
- `password` — at least 8 characters.

**Success response (`201`):**

- `success: true`, `message`, `displayUi`.
- `data.user` — `id`, `username`, `email`, `isActive`, `createdAt`.
- `data.accessToken` — JWT access token, 15-minute expiry.
- `data.tokenType` — `bearer`.
- `data.expiresIn` — access token lifetime in seconds.
- `Set-Cookie` — `refresh_token`, `HttpOnly`, `Secure`, `SameSite`, `Path=/auth`, 90-day `Max-Age`.

**Execution flow:**

1. Request body is validated (required fields, username rules, email format, password length).
2. Email is normalized (trimmed and lowercased).
3. The service opens an async database session and checks whether the email or username already exists.
4. The password is hashed with bcrypt.
5. A new user row is created with a UUIDv7 identifier.
6. An access token is generated with `sub`, `jti`, `type`, `iat`, `exp`, `iss`, and `aud` claims.
7. An opaque refresh token is generated; its SHA-256 hash is stored with `familyId`, `slidingExpiry = now + 30 days`, `absoluteExpiry = now + 90 days`, `revoked = false`, and client audit fields.
8. The transaction is committed once; failures are rolled back.
9. The controller returns the camelCase success payload, sets the refresh cookie, and returns the response.

**Error cases:**

- `409` — email or username already exists.
- `422` — validation failure (invalid email, weak username, short password).
- `500` — unexpected server or database failure.

### Endpoint 2 — POST /auth/login

**Description:**

Authenticates an existing user with a username and password. The server looks up the user by username, verifies the submitted password against the stored bcrypt hash, issues a new 15-minute JWT access token in the JSON body, and issues a new opaque refresh token inside an httpOnly cookie. The refresh token is stored hashed in the database with a new `familyId`, a 30-day sliding expiry, a fixed 90-day absolute expiry, and `revoked = false`.

**Request body (JSON, camelCase):**

- `username` — the account username (required).
- `password` — the account password (required).

**Success response (`200`):**

- `success: true`, `message`, `displayUi`.
- `data.user` — `id`, `username`, `email`, `isActive`, `createdAt`.
- `data.accessToken` — JWT access token, 15-minute expiry.
- `data.tokenType` — `bearer`.
- `data.expiresIn` — access token lifetime in seconds.
- `Set-Cookie` — `refresh_token`, `HttpOnly`, `Secure`, `SameSite`, `Path=/auth`, 90-day `Max-Age`.

**Execution flow:**

1. Request body is validated (username and password are required).
2. The service opens an async database session and looks up the user by the trimmed username.
3. The submitted password is verified against the stored bcrypt hash with a constant generic failure message.
4. If the user is inactive, the request is rejected.
5. An access token is generated with `sub`, `jti`, `type`, `iat`, `exp`, `iss`, and `aud` claims.
6. A new opaque refresh token is generated; its SHA-256 hash is stored with a new `familyId`, `slidingExpiry = now + 30 days`, `absoluteExpiry = now + 90 days`, `revoked = false`, and client audit fields.
7. The transaction is committed once; failures are rolled back.
8. The controller returns the camelCase success payload, sets the refresh cookie, and returns the response.

**Error cases:**

- `401` — invalid username or password.
- `403` — account is inactive.
- `422` — validation failure (missing username or password).
- `500` — unexpected server or database failure.
