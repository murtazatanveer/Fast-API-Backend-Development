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

In this project, we have two modules: `/auth` and `/patients`.

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

## 5. Project Details and JWT Two-Factor Authentication

1. Signup
   User submits credentials (Username , Email, Password).

Server validates input and hashes the password.

Server saves the user directly to the DB. (No is_email_verified column, no OTP sent, no tokens issued).

Server returns 200 OK.

Client redirects the user to the Login flow.

2. Login (With 2-Min OTP)
   User submits Username and Password.

Server validates the password (hash comparison).

Server generates a 6-digit OTP, hashes it, and stores it in the DB in the Otps table with expires_at = now + 2 minute and attempts = 0.

Server emails the plaintext OTP to the user.

Server returns 200 OK (No tokens issued yet).

Client prompts for OTP. User submits OTP. Client calls POST /auth/verify-login.

Server checks the OTP:

On the client sidee OTP Screen is displayed, When the OTP screen is displayed and the user submits a code, the server validates the request. If the user enters an incorrect OTP three times, the server deletes the OTP entirely and returns a 401 Unauthorized response. Similarly, if the OTP exceeds its 2-minute expiration window, the server also returns a 401 Unauthorized response. However, if the user enters the correct OTP within the 3-attempt limit and before the 2-minute timer expires, the server deletes the OTP row from the database and successfully generates the access and refresh tokens.

If valid: Burns the OTP. Server generates two tokens:

Access token — JWT, 15 min expiry, returned in JSON body.

Refresh token — opaque or JWT, sent as an httpOnly cookie.

Server stores the refresh token hashed in DB with:

sliding_expiry = now + 30 days

absolute_expiry = now + 90 days ← set once, never changes

family_id (for reuse detection)

revoked = false

Cookie set with: httpOnly; Secure; SameSite=Strict/Lax;

Client stores access token in React Context (in-memory, never localStorage).

"OTP Upsert Logic: The /auth/login endpoint must use a database UPSERT operation (or equivalent logic) on the user_id when generating a new OTP. If an OTP row already exists for the user, the server must overwrite the existing otp_hash, reset the expires_at to now + 2 minutes, and reset the attempts counter back to 0. This ensures that a user only ever has exactly one active OTP row in the database at any given time, preventing duplicate rows if the user clicks 'Resend OTP' or logs in multiple times."

3. Normal API calls (access token valid)
   Client attaches authToken: Bearer\_<access_token>.

Server verifies JWT signature, exp, aud, iss.

Response returned.

4. Access token expires (in-session)
   Server returns 401.

Client 401 interceptor (not a client-side exp check) uses a single in-flight refresh promise and calls POST /auth/refresh once with the cookie. Concurrent 401 responses must await the same promise, and a response must retry with the newer access token instead of refreshing again if the token has already changed.

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

Client updates Context with new access token, retries all original requests. Refresh failure is handled through one shared session-expiry path so concurrent failures do not schedule multiple redirects or toasts. (User bypasses 2FA here).

5. User closes page and reopens later
   Access token in memory is null.

On app mount, client calls POST /auth/refresh once (deduplicated — single in-flight promise).

Server performs the same checks as step 4:

If sliding_expiry expired (inactive > 30 days) → 401 → user goes to Login (Step 2) and gets a new OTP.

If absolute_expiry expired (session > 90 days) → 401 → user goes to Login (Step 2) and gets a new OTP.

Otherwise → rotate token, slide 30 days forward, keep 90-day absolute, return new access token.

User is silently logged in.

6. Logout
   Client calls DELETE /auth/logout.

Server deletes/revokes the refresh token row in DB.

Server clears the cookie.

Client clears Context. (Client-only clearing is not sufficient — server revocation is required.)

HTTP methods:

/auth/login and /auth/verify-login (it is the endpoint for the otp) use POST.

/auth/refresh remains POST because it rotates state.

/auth/logout and /auth/logout-other-devices use DELETE.

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

## 9. Local Development and Deployment Configuration

### Local Development

The frontend runs at `http://localhost:5173` and the backend runs at
`http://localhost:8000`. Requests are cross-origin because the ports differ,
but they are same-site because both use `localhost`.

CORS configuration in `main.py`:

- `allow_origins=["http://localhost:5173"]`
- `allow_credentials=True`
- `allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]`
- `allow_headers=["Content-Type", "authToken"]`

`User-Agent` and the client IP address must not be added to `allow_headers`.
`User-Agent` is sent automatically by the browser, and the IP address is
derived from the connection rather than a request header. `Set-Cookie` must
not be added to `expose_headers` because browsers do not expose that forbidden
response header to JavaScript.

Frontend requests that use the refresh cookie must send credentials:

- `fetch`: `credentials: "include"`
- Axios: `withCredentials: true`

Refresh calls must be deduplicated with a single in-flight promise. Concurrent 401 responses must await the same promise instead of sending multiple `POST /auth/refresh` requests.

Local `Configuration/.env` cookie values:

- `REFRESH_COOKIE_SECURE=False`
- `REFRESH_COOKIE_SAMESITE=lax`

Local `Configuration/.env` OTP and email values:

- `RESEND_API_KEY` — Resend API key.
- `OTP_FROM_EMAIL` — verified sender address; use `onboarding@resend.dev` for local testing.
- `OTP_EXPIRE_MINUTES=2`
- `OTP_MAX_ATTEMPTS=3`

Use `localhost` consistently for both frontend and backend. Do not mix
`localhost` and `127.0.0.1`, because that changes the cookie site.

### Deployment

CORS `allow_origins` must contain the exact production frontend origin.
`allow_credentials` remains `True`. Wildcard origins must not be used with
credentials.

HTTPS is mandatory because the refresh cookie uses `Secure=True`.

#### Same-site deployment

Use `REFRESH_COOKIE_SECURE=True` and `REFRESH_COOKIE_SAMESITE=lax`.

Example: `app.example.com` and `api.example.com`.

#### Different-site deployment

Use `REFRESH_COOKIE_SECURE=True` and `REFRESH_COOKIE_SAMESITE=none`.

Example: `frontend.vercel.app` and `backend.onrender.com`.

Different-site cookies are third-party cookies and may be blocked by browsers.
Prefer serving the API through the frontend domain or using subdomains of one
registrable domain.

If the backend is behind a reverse proxy, configure trusted forwarded headers
to record the real client IP. This is separate from CORS and does not require
adding `X-Forwarded-For` to `allow_headers`.

### Cookie Properties

- `HttpOnly=True`
- `Secure` is environment-driven
- `SameSite` is environment-driven
- Host-only cookie; no `Domain`
- No explicit `Path`; browsers default it to `/auth`
- `Max-Age=90 days`
- The refresh token is never exposed to JavaScript

## Endpoints Architecture

### Endpoint 1 — POST /auth/signup

**Description:**

Registers a new user account. The server validates the submitted username, email, and password, hashes the password with bcrypt, and creates the user. No OTP is sent, and no access token, refresh token, or refresh cookie is issued. The API responds with a success message only.

**Request body (JSON, camelCase):**

- `username` — at least 8 characters, must contain at least one uppercase letter, one digit, and one special character.
- `email` — valid email address, unique in the system.
- `password` — at least 8 characters.

**Success response (`200`):**

- `success: true`, `message` (`Account Created Successfully`), `displayUi`.
- No `data`, tokens, or user data are returned.
- No `Set-Cookie` header is sent.

**Execution flow:**

1. Request body is validated (required fields, username rules, email format, password length).
2. Email is normalized (trimmed and lowercased); the username is trimmed.
3. The service opens an async database session and checks whether the email or username already exists.
4. The password is hashed with bcrypt.
5. A new user row is created with a UUIDv7 identifier.
6. The transaction is committed once; failures are rolled back, and a unique-constraint race is reported as a duplicate account.
7. The controller returns the success message without tokens or a refresh cookie.

**Error cases:**

- `409` — email or username already exists.
- `422` — validation failure (invalid email, weak username, short password).
- `500` — unexpected server or database failure.

### Endpoint 2 — POST /auth/login

**Description:**

Authenticates an existing user with a username and password. On success, the server generates a six-digit OTP, hashes it with bcrypt, upserts the single OTP row for the user, emails the plaintext OTP to the user's registered email, and returns a masked email address. No access token, refresh token, or refresh cookie is issued. Calling the endpoint again acts as a resend and invalidates the previous OTP.

**Request body (JSON, camelCase):**

- `username` — the account username (required).
- `password` — the account password (required).

**Success response (`200`):**

- `success: true`, `message` (`OTP Sent Successfully`), `displayUi`, `data.email` (masked registered email).
- No access token or refresh token is returned.
- No `Set-Cookie` header is sent.

**Execution flow:**

1. Request body is validated (username and password are required).
2. The service opens an async database session and looks up the user by the trimmed username.
3. The submitted password is verified against the stored bcrypt hash with a constant generic failure message; no OTP is created on failure.
4. A six-digit OTP is generated with leading zeros preserved and hashed with bcrypt.
5. The service upserts the user's single `Otps` row by `userId`:
   - Overwrites `otpHash`.
   - Sets `expiresAt = now + 2 minutes`.
   - Resets `attempts = 0`.
   - Preserves the existing row `id` and `createdAt`.
6. The transaction is committed once; failures are rolled back.
7. The plaintext OTP is emailed to the user's registered email through Resend.
8. If email sending fails, the OTP row is deleted in a best-effort cleanup transaction and the request fails.
9. The controller returns the success message and masked email only.

**Error cases:**

- `401` — invalid username or password.
- `422` — validation failure (missing username or password).
- `500` — unexpected server, database, or email failure. If email delivery fails after the OTP commit, the OTP row is removed.

### Endpoint 3 — POST /auth/verify-login

**Description:**

Verifies the OTP issued by `POST /auth/login`. The server looks up the user by username, locks the user's OTP row with `SELECT ... FOR UPDATE`, and validates expiry, attempt count, and the bcrypt OTP hash. A successful verification deletes the OTP, issues a 15-minute access token, and creates a new refresh-token row inside an httpOnly cookie with a new `familyId`, a 30-day sliding expiry, and a fixed 90-day absolute expiry.

**Request body (JSON, camelCase):**

- `username` — the account username (required).
- `otp` — exactly six digits, matching `^\d{6}$`.

**Success response (`200`):**

- `success: true`, `message` (`User Login Successfully`), `displayUi`, `data.accessToken`.
- No user data is included in the JSON body; the refresh token is never exposed in JSON.
- `Set-Cookie` — `refresh_token`, `HttpOnly`, `Secure`, `SameSite`, 90-day `Max-Age`.

**Execution flow:**

1. Request body is validated.
2. The service opens an async database session and looks up the user by the trimmed username.
3. If the user does not exist, the request fails with `401`.
4. The user's OTP row is selected by `userId` using a row lock (`SELECT ... FOR UPDATE`) to serialize concurrent verification attempts.
5. If no OTP row exists, the request fails with `401`.
6. If `expiresAt` is not after the current time, the OTP row is deleted, the transaction is committed, and the request fails with `401`.
7. If the submitted OTP does not match the stored bcrypt hash:
   - `attempts` is incremented.
   - If `attempts` reaches the configured maximum of 3, the OTP row is deleted.
   - The transaction is committed and the request fails with `401`.
8. If the OTP is correct and within the limit and expiry:
   - The OTP row is deleted.
   - A 15-minute access token is issued.
   - A new refresh-token row is created with a new `familyId`, `slidingExpiry = now + 30 days`, `absoluteExpiry = now + 90 days`, `revoked = false`, and client audit fields.
   - The transaction is committed.
9. The controller returns the success message and access token, sets the refresh cookie, and returns the response.

**Error cases:**

- `401` — user not found, no OTP row, expired OTP, incorrect OTP, or the attempt limit reached; the message is `Invalid or expired OTP`.
- `422` — validation failure (missing username or invalid OTP format).
- `500` — unexpected server or database failure.

### Endpoint 4 — POST /auth/refresh

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

### Endpoint 5 — DELETE /auth/logout

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

### Endpoint 6 — DELETE /auth/logout-other-devices

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

### Endpoint 7 — POST /patients

**Description:**

Registers a patient owned by the authenticated user. The client supplies the patient identifier, which must match `^P\d{3}$` and is globally unique. The server validates all patient fields, computes the BMI and verdict, stores the patient together with the stored BMI, verdict, and the authenticated user's ID as `createdBy` in the `Patients` table, and returns the patient identifier together with a synthetic Firestore-compatible document path (`Patients/{patientId}`). Patients are linked to `Users.id` with `ON DELETE CASCADE`.

**Request body (JSON, camelCase):**

- `id` — patient identifier, must match `^P\d{3}$` (for example `P001`).
- `name` — at most 50 characters.
- `city` — at most 50 characters.
- `age` — integer greater than 0 and less than 81.
- `gender` — one of `male`, `female`, `other`.
- `height` — positive number, in meters.
- `weight` — positive number, in kilograms.

**Success response (`201`):**

- `success: true`, `message` (`Patient Created Successfully`), `displayUi: true`.
- `data.docId` — the patient ID.
- `data.docPath` — `Patients/{patientId}`.
- `data.createdBy` — the authenticated user's UUID as a string.
- No patient fields are returned.

**Execution flow:**

1. The JWT dependency validates the `authToken` header and resolves the authenticated user.
2. The request body is validated, including the patient ID pattern and all patient constraints.
3. The service opens an async database session and checks whether the patient ID already exists globally.
4. The BMI and verdict are computed from the submitted height and weight.
5. A new `Patients` row is created with the submitted fields, computed BMI and verdict, and `createdBy` set from the access token.
6. The transaction is committed once; failures are rolled back, and a unique-constraint race is reported as a duplicate patient.

**Error cases:**

- `409` — a patient with the same ID already exists (`Patient ID already exists`).
- `422` — validation failure (invalid patient ID, age, gender, height, weight, or field limits), or the `authToken` header is missing.
- `401` — the `authToken` value is invalid.
- `500` — unexpected server or database failure (`Internal Server Error`).

### Endpoint 8 — GET /patients

**Description:**

Returns every patient created by the authenticated user. Results are ordered by patient ID ascending for deterministic output. Each item contains the patient ID, patient fields, stored BMI and verdict, and `createdBy`.

**Request:**

- `authToken` header — `Bearer_<accessToken>` (required).
- No request body or query parameters.

**Success response (`200`):**

- `success: true`, `message` (`Patients fetched successfully`), `displayUi: false`.
- `data` — a list of patient objects; the list is empty when the user has no patients.

**Execution flow:**

1. The JWT dependency validates the access token and resolves the authenticated user.
2. The service opens an async database session and selects patients whose `createdBy` equals the authenticated user's ID.
3. Results are ordered by patient ID ascending.
4. Each row is serialized with camelCase keys, including `bmi`, `verdict`, and `createdBy`.

**Error cases:**

- `422` — the `authToken` header is missing.
- `401` — the `authToken` value is invalid.
- `500` — unexpected server or database failure (`An error occurred while fetching patients`).

### Endpoint 9 — GET /patients/sorted

**Description:**

Returns the authenticated user's patients sorted by height, weight, or BMI in ascending or descending order. The requested sort field direction is applied first, and patient ID ascending is used as a deterministic tiebreaker. Results are limited to patients created by the authenticated user.

**Request:**

- `authToken` header — `Bearer_<accessToken>` (required).
- Query parameter `sortBy` — required; one of `height`, `weight`, `bmi`.
- Query parameter `order` — optional; one of `asc` (default) or `desc`.

**Success response (`200`):**

- `success: true`, `message` (`Patients sorted by {sortBy} in {order} order`), `displayUi: false`.
- `data` — the sorted list of patient objects.

**Execution flow:**

1. The JWT dependency validates the access token and resolves the authenticated user.
2. The service validates `sortBy` against the allowed fields and returns `400` on failure; it then validates `order` against the allowed directions.
3. The service opens an async database session and selects the authenticated user's patients, ordering by the requested stored column and then patient ID ascending.
4. Each row is serialized with camelCase keys.

**Error cases:**

- `400` — invalid `sortBy` (`Invalid sortBy field. Select from ['height', 'weight', 'bmi']`) or invalid `order` (`Invalid order field. Select from ['asc', 'desc']`).
- `422` — the required `sortBy` query parameter or the `authToken` header is missing, or the `authToken` value is invalid.
- `500` — unexpected server or database failure (`An error occurred while sorting patients`).

### Endpoint 10 — GET /patients/{patientId}

**Description:**

Returns a single patient by ID. Access is owner-scoped: the patient must have been created by the authenticated user; otherwise the endpoint responds as if the patient does not exist. The response includes the patient ID, patient fields, stored BMI and verdict, and `createdBy`.

**Request:**

- `authToken` header — `Bearer_<accessToken>` (required).
- Path parameter `patientId` — required; must match `^P\d{3}$`.
- No request body.

**Success response (`200`):**

- `success: true`, `message` (`Patient Found`), `displayUi: true`.
- `data` — the patient object with camelCase keys.

**Execution flow:**

1. The JWT dependency validates the access token and resolves the authenticated user.
2. The path parameter is validated against the patient ID pattern.
3. The service opens an async database session and selects the patient by ID and matching `createdBy`.
4. If no row is found, the service fails with `404`; otherwise the row is serialized.

**Error cases:**

- `404` — the patient does not exist or belongs to another user (`Patient ID does not exist`).
- `422` — invalid patient ID format, missing `authToken` header, or invalid `authToken` value.
- `500` — unexpected server or database failure (`An error occurred while fetching the patient`).

### Endpoint 11 — PUT /patients/{patientId}

**Description:**

Partially updates a patient owned by the authenticated user. Only non-null submitted fields are applied. The current patient fields are merged with the submitted changes, the BMI and verdict are recomputed, and both are stored alongside the submitted changes. The response reports the updated patient ID and the names of the fields supplied by the client.

**Request body (JSON, camelCase):**

- `name`, `city`, `age`, `gender`, `height`, `weight` — all optional; each follows the same constraints as creation. Explicit `null` values are treated as absent.

**Success response (`200`):**

- `success: true`, `message` (`Patient updated successfully`), `displayUi: true`.
- `data.docId` — the patient ID.
- `data.updatedFields` — the list of client-supplied field names.

**Execution flow:**

1. The JWT dependency validates the access token and resolves the authenticated user.
2. The path parameter is validated against the patient ID pattern, and the request body is validated.
3. The service removes null fields; if no fields remain, it fails with `400`.
4. The service opens an async database session and selects the patient by ID and matching `createdBy` using a row lock.
5. If no row is found, the service fails with `404`.
6. The existing values are merged with the submitted changes, and the resulting patient is revalidated to recompute BMI and verdict.
7. The submitted fields and recomputed BMI and verdict are written, the transaction is committed, and the updated field names are returned.

**Error cases:**

- `404` — the patient does not exist or belongs to another user (`Patient ID does not exist`).
- `400` — no non-null fields were supplied (`No fields to update`).
- `422` — invalid patient ID format, invalid field values, missing `authToken` header, or invalid `authToken` value.
- `500` — unexpected server or database failure (`An error occurred while updating the patient`).

### Endpoint 12 — DELETE /patients/{patientId}

**Description:**

Deletes a patient owned by the authenticated user. Access is owner-scoped, so another user's patient is treated as nonexistent. The response returns the deleted patient's ID.

**Request:**

- `authToken` header — `Bearer_<accessToken>` (required).
- Path parameter `patientId` — required; must match `^P\d{3}$`.
- No request body.

**Success response (`200`):**

- `success: true`, `message` (`Patient Deleted Successfully`), `displayUi: true`.
- `data.docId` — the deleted patient ID.

**Execution flow:**

1. The JWT dependency validates the access token and resolves the authenticated user.
2. The path parameter is validated against the patient ID pattern.
3. The service opens an async database session and selects the patient by ID and matching `createdBy`.
4. If no row is found, the service fails with `404`.
5. The row is deleted, the transaction is committed, and the patient ID is returned.

**Error cases:**

- `404` — the patient does not exist or belongs to another user (`Patient ID does not exist`).
- `422` — invalid patient ID format, missing `authToken` header, or invalid `authToken` value.
- `500` — unexpected server or database failure (`An error occurred while deleting the patient`).
