# Patients CRUD API — Endpoint Reference

FastAPI backend for the Patients CRUD application (JWT authentication + Firestore).

- **Base URL (local):** `http://localhost:8000`
- **App title:** `Patients CRUD API` · **Version:** `1.0.0`
- **CORS allowed origin:** `http://localhost:5173` (with credentials)
- **Source of truth:** `main.py`, `routes/authRoutes.py`, `Controllers/authController.py`

---

## Authentication

### Access token (JWT)

Protected endpoints require a custom header:

```
authToken: Bearer_<jwt-access-token>
```

The backend enforces the `Bearer_` prefix (note the underscore, not a space). The token is decoded to obtain the `uid` claim, then the user is verified against the Firestore `Users` collection.

### Refresh token

`/auth/signup`, `/auth/login` set an **httpOnly cookie** named `refreshToken`. The cookie is used by `/auth/refresh` and is deleted by `/auth/logout`. Because it is httpOnly, frontend code cannot read it; browser requests to these endpoints must include credentials.

### Standard response envelope

Success responses (most endpoints):

```json
{
  "success": true,
  "message": "Patients fetched successfully",
  "displayUi": false,
  "data": {}
}
```

Error responses:

```json
{
  "success": false,
  "message": "Patient ID already exists",
  "displayUi": true
}
```

- `displayUi` is a backend hint telling the frontend whether the message should be shown to the user.
- Some auth handlers (login/signup) return a raw dict instead of using the helper, and a few responses omit `displayUi` (documented per endpoint below).

---

## Endpoint Summary

| # | Method | Path | Auth | Purpose |
|---|--------|------|------|---------|
| 1 | GET | `/` | Public | Welcome / health message |
| 2 | POST | `/auth/signup` | Public | Register a user |
| 3 | POST | `/auth/login` | Public | Log in a user |
| 4 | PUT | `/auth/refresh` | Refresh cookie | Issue a new access token |
| 5 | DELETE | `/auth/logout` | JWT + refresh cookie | Log out current device |
| 6 | DELETE | `/auth/logout-other-devices` | JWT + refresh cookie | Revoke all other sessions |
| 7 | POST | `/create-patient` | JWT | Create a patient |
| 8 | GET | `/patients` | JWT | List the user's patients |
| 9 | GET | `/sort-patients` | JWT | List patients sorted by field |
| 10 | GET | `/patient/{patientId}` | JWT | Get a single patient |
| 11 | PUT | `/update-patient/{patientId}` | JWT | Partially update a patient |
| 12 | DELETE | `/delete-patient/{patientId}` | JWT | Delete a patient |

> The `/auth/*` paths come from `routes/authRoutes.py` (`prefix="/auth"`) + `Controllers/authController.py`. All patient endpoints are declared directly on the app in `main.py`.

---

## 1. GET `/`

**Auth:** None

**Description:** Welcome/health message.

**Response `200 OK`:**

```json
{
  "message": "Welcome to Patients CRUD App Using Firestore",
  "success": true
}
```

---

## 2. POST `/auth/signup`

**Auth:** None
**Body:** `UserRegister`

| Field | Type | Constraints |
|-------|------|-------------|
| `username` | string | required, 8–30 chars |
| `email` | string (email) | required, valid email |
| `password` | string | required, 8–20 chars |

**Side effects:** creates the user in Firestore, creates a refresh token document, and sets the `refreshToken` httpOnly cookie.

**Response `201 Created`:**

```json
{
  "success": true,
  "message": "Account created successfully",
  "displayUi": true,
  "data": {
    "accessToken": "<jwt>",
    "user": {
      "id": "<userId>",
      "username": "johndoe",
      "email": "john@example.com"
    }
  }
}
```

**Errors:**

| Status | Message | `displayUi` |
|--------|---------|-------------|
| 409 | `Username or Email already exists` | true |
| 422 | Pydantic validation error | — |
| 500 | `Internal Server Error ...` | false |

---

## 3. POST `/auth/login`

**Auth:** None
**Body:** `UserLogin`

| Field | Type | Constraints |
|-------|------|-------------|
| `username` | string | required, 8–30 chars |
| `password` | string | required, 8–20 chars |

**Side effects:** verifies password, creates a refresh token document, sets the `refreshToken` httpOnly cookie.

**Response `200 OK`:**

```json
{
  "success": true,
  "message": "Logged in successfully",
  "displayUi": true,
  "data": {
    "accessToken": "<jwt>",
    "user": {
      "id": "<userId>",
      "username": "johndoe",
      "email": "john@example.com"
    }
  }
}
```

**Errors:**

| Status | Message | `displayUi` |
|--------|---------|-------------|
| 401 | `Invalid username or password` | true |
| 422 | Pydantic validation error | — |
| 500 | `Internal Server Error ...` | false |

---

## 4. PUT `/auth/refresh`

**Auth:** `refreshToken` httpOnly cookie (no body, no JWT header)
**Body:** None

**Description:** Looks up the refresh token in Firestore, validates expiry and user existence, and issues a new access token. The refresh cookie is **not** rotated.

**Response `200 OK`:**

```json
{
  "success": true,
  "message": "Token refreshed successfully",
  "data": {
    "accessToken": "<new-jwt>",
    "user": {
      "id": "<userId>",
      "username": "johndoe",
      "email": "john@example.com"
    }
  }
}
```

**Errors:**

| Status | Message | `displayUi` |
|--------|---------|-------------|
| 401 | `No refresh token provided` | false (omitted) |
| 401 | `Invalid refresh token` | false (omitted) |
| 401 | `Refresh token expired. Please log in again.` | false (omitted) |
| 401 | `User account no longer exists` | false (omitted) |

> **Implementation note:** the `except` block calls `errorResponse(...)` without returning it, so unexpected exceptions do not produce the intended 500 response.

---

## 5. DELETE `/auth/logout`

**Auth:** JWT (`authToken` header) **and** `refreshToken` cookie
**Body:** None

**Description:** Verifies the refresh token belongs to the authenticated user, deletes it from Firestore, and clears the cookie.

**Response `200 OK`:**

```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

> **Implementation note:** no `displayUi` field is returned here.

**Errors:**

| Status | Message |
|--------|---------|
| 401 | `No refresh token provided` |
| 401 | `Invalid or already revoked token` |
| 401 | `Token does not belong to this user` |
| 401 | Missing/invalid JWT from `getCurrentUser` |
| 500 | Internal error (handler currently does not return the response) |

---

## 6. DELETE `/auth/logout-other-devices`

**Auth:** JWT (`authToken` header) **and** current `refreshToken` cookie
**Body:** None

**Description:** Verifies the current refresh token, then batch-deletes all other refresh tokens belonging to the same user. The current device stays logged in.

**Response `200 OK`:**

```json
{
  "success": true,
  "message": "Logged out from 2 other devices successfully",
  "displayUi": true
}
```

**Errors:**

| Status | Message |
|--------|---------|
| 401 | `No refresh token provided` |
| 401 | `Invalid session token` |
| 401 | `Token mismatch` |
| 401 | Missing/invalid JWT from `getCurrentUser` |
| 500 | Internal error (handler currently does not return the response) |

---

## 7. POST `/create-patient`

**Auth:** JWT required
**Body:** `Patient`

| Field | Type | Constraints |
|-------|------|-------------|
| `id` | string | required, pattern `^P\d{3}$` (e.g. `P001`) |
| `name` | string | required, max 50 chars |
| `city` | string | required, max 50 chars |
| `age` | integer | required, `> 0` and `< 81`, strict |
| `gender` | string | required, one of `male`, `female`, `other` |
| `height` | float | required, `> 0` (meters), strict |
| `weight` | float | required, `> 0` (kg), strict |
| `bmi` | float | computed (read-only) = `weight / height²`, rounded to 2 |
| `verdict` | string | computed (read-only): `Underweight`, `Normal`, `Overweight`, `Obese` |

**Side effects:** stores the patient in the `Patients` collection with `createdBy = <currentUserId>`. The document ID equals `id`.

**Response `201 Created`:**

```json
{
  "success": true,
  "message": "Patient Created Successfully",
  "displayUi": true,
  "data": {
    "docId": "P001",
    "docPath": "Patients/P001",
    "createdBy": "<userId>"
  }
}
```

**Errors:**

| Status | Message | `displayUi` |
|--------|---------|-------------|
| 401 | Missing/invalid JWT | — |
| 409 | `Patient ID already exists` | true |
| 422 | Pydantic validation error | — |
| 500 | `Internal Server Error` | true |

---

## 8. GET `/patients`

**Auth:** JWT required
**Query params:** None

**Description:** Returns only patients whose `createdBy` matches the authenticated user.

**Response `200 OK`:**

```json
{
  "success": true,
  "message": "Patients fetched successfully",
  "displayUi": false,
  "data": [
    {
      "id": "P001",
      "name": "Ali Khan",
      "city": "Lahore",
      "age": 30,
      "gender": "male",
      "height": 1.75,
      "weight": 70,
      "bmi": 22.86,
      "verdict": "Normal",
      "createdBy": "<userId>"
    }
  ]
}
```

**Errors:**

| Status | Message | `displayUi` |
|--------|---------|-------------|
| 401 | Missing/invalid JWT | — |
| 500 | `An error occurred while fetching patients` | false |

---

## 9. GET `/sort-patients`

**Auth:** JWT required

**Query params:**

| Param | Type | Required | Allowed values | Default |
|-------|------|----------|----------------|---------|
| `sortBy` | string | yes | `height`, `weight`, `bmi` | — |
| `order` | string | no | `asc`, `desc` | `asc` |

**Description:** Returns the user's patients ordered by the selected field.

**Example:** `GET /sort-patients?sortBy=bmi&order=desc`

**Response `200 OK`:** same envelope and `data` shape as `/patients`.

```json
{
  "success": true,
  "message": "Patients sorted by bmi in desc order",
  "displayUi": false,
  "data": []
}
```

**Errors:**

| Status | Message | `displayUi` |
|--------|---------|-------------|
| 400 | `Invalid sortBy field. Select from ['height', 'weight', 'bmi']` | true |
| 400 | `Invalid order field. Select from ['asc', 'desc']` | true |
| 401 | Missing/invalid JWT | — |
| 500 | `An error occurred while sorting patients` | false |

---

## 10. GET `/patient/{patientId}`

**Auth:** JWT required

**Path params:**

| Param | Type | Constraints |
|-------|------|-------------|
| `patientId` | string | pattern `^P\d{3}$` |

**Response `200 OK`:**

```json
{
  "success": true,
  "message": "Patient Found",
  "displayUi": true,
  "data": {
    "id": "P001",
    "name": "Ali Khan",
    "city": "Lahore",
    "age": 30,
    "gender": "male",
    "height": 1.75,
    "weight": 70,
    "bmi": 22.86,
    "verdict": "Normal",
    "createdBy": "<userId>"
  }
}
```

**Errors:**

| Status | Message | `displayUi` |
|--------|---------|-------------|
| 401 | Missing/invalid JWT | — |
| 404 | `Patient ID does not exist` | true |
| 422 | Invalid path format | — |
| 500 | `An error occurred while fetching the patient` | false |

> **Note:** the lookup does not filter by owner; any authenticated user who knows a patient ID can read it.

---

## 11. PUT `/update-patient/{patientId}`

**Auth:** JWT required

**Path params:**

| Param | Type | Constraints |
|-------|------|-------------|
| `patientId` | string | pattern `^P\d{3}$` |

**Body:** `UpdatePatient` — all fields optional; only provided fields are updated.

| Field | Type | Constraints |
|-------|------|-------------|
| `name` | string | optional, max 50 |
| `city` | string | optional, max 50 |
| `age` | integer | optional, `> 0` and `< 81`, strict |
| `gender` | string | optional, `male` / `female` / `other` |
| `height` | float | optional, `> 0`, strict |
| `weight` | float | optional, `> 0`, strict |

**Side effects:** merges updates into the existing document and recomputes `bmi` and `verdict`.

**Example body:**

```json
{
  "city": "Karachi",
  "weight": 75.5
}
```

**Response `200 OK`:**

```json
{
  "success": true,
  "message": "Patient updated successfully",
  "displayUi": true,
  "data": {
    "docId": "P001",
    "updatedFields": ["city", "weight"]
  }
}
```

**Errors:**

| Status | Message | `displayUi` |
|--------|---------|-------------|
| 400 | `No fields to update` | true |
| 401 | Missing/invalid JWT | — |
| 404 | `Patient ID does not exist` | true |
| 422 | Invalid path/body format | — |
| 500 | `An error occurred while updating the patient` | false |

> **Note:** like `GET /patient/{patientId}`, update does not verify the document's `createdBy` owner.

---

## 12. DELETE `/delete-patient/{patientId}`

**Auth:** JWT required

**Path params:**

| Param | Type | Constraints |
|-------|------|-------------|
| `patientId` | string | pattern `^P\d{3}$` |

**Response `200 OK`:**

```json
{
  "success": true,
  "message": "Patient Deleted Successfully",
  "displayUi": true,
  "data": {
    "docId": "P001"
  }
}
```

**Errors:**

| Status | Message | `displayUi` |
|--------|---------|-------------|
| 401 | Missing/invalid JWT | — |
| 404 | `Patient ID does not exist` | true |
| 422 | Invalid path format | — |
| 500 | `An error occurred while deleting the patient` | false |

> **Note:** delete does not verify the document's `createdBy` owner.

---

## Data Models

### `UserRegister`

```json
{
  "username": "johndoe1",
  "email": "john@example.com",
  "password": "secret123"
}
```

### `UserLogin`

```json
{
  "username": "johndoe1",
  "password": "secret123"
}
```

### `Patient` (create)

```json
{
  "id": "P001",
  "name": "Ali Khan",
  "city": "Lahore",
  "age": 30,
  "gender": "male",
  "height": 1.75,
  "weight": 70
}
```

Computed fields returned by the API:

- `bmi = round(weight / height², 2)`
- `verdict`:
  - `bmi < 18.5` → `Underweight`
  - `bmi < 25` → `Normal`
  - `bmi < 30` → `Overweight`
  - otherwise → `Obese`

### `UpdatePatient`

All fields optional: `name`, `city`, `age`, `gender`, `height`, `weight`.

---

## HTTP Status Codes Used

| Code | Meaning in this API |
|------|---------------------|
| 200 | Success (read/update/delete/login/refresh/logout) |
| 201 | Created (signup, create-patient) |
| 400 | Invalid query params or empty update payload |
| 401 | Invalid credentials, missing/invalid/expired token |
| 404 | Patient not found |
| 409 | Duplicate username/email or patient ID |
| 422 | Pydantic/FastAPI validation failure |
| 500 | Internal server error |

---

## Inconsistencies Noted While Documenting

1. `/auth/refresh` error responses omit `displayUi` (helper default `false`), and its exception handler calls `errorResponse(...)` without returning it.
2. `/auth/logout` success response omits `displayUi`.
3. `/auth/signup` and `/auth/login` return raw dicts instead of the shared `successResponse` helper; `/auth/logout` and `/auth/logout-other-devices` exception handlers also miss a `return`.
4. The auth header uses a non-standard scheme (`authToken: Bearer_<jwt>`).
5. The refresh cookie is set with `secure=False` and `samesite="lax"` (development settings).
6. Patient read/update/delete endpoints do not enforce ownership, while `/patients` and `/sort-patients` do filter by `createdBy`.
