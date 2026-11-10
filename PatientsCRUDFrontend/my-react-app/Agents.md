# Patients Management System using JWT Two-Factor Authentication

## Project Description and Workflow

### Authentication Module (Login and Signup Pages)

#### 1. Application Initialization and Root URL

When the application starts, the `AuthProvider` calls `POST /auth/refresh` once.

- If the refresh succeeds, the new access token is stored in the global authentication Context.
- If the refresh fails, the access token is set to `null`.
- Startup refresh failures are handled silently.
- While initialization is running, protected and public routes display a session-checking loading screen.
- Concurrent startup refreshes are deduplicated by a single in-flight refresh promise.

The access token is kept only in memory. It is never written to `localStorage`.

When a user accesses the root URL (`/`), they are redirected to the `/login` route.

The `/login` route is a public route. However, if an access token is present in the global authentication Context, the user is redirected to the `/dashboard` route.

The `/signup` route is also public and follows the same redirect rule.

#### 2. User Signup

The user submits a username, email address, and password.

On successful signup:

- No access token is stored.
- No refresh token is stored.
- No refresh cookie is issued.
- The user is navigated to the `/login` route.
- The Login page displays the account-creation success message.

#### 3. User Login and OTP Transition

The user submits a username and password on the Login page.

On successful login:

- No access token is stored yet.
- No refresh cookie is issued yet.
- The Login page replaces the credentials form with the OTP module.
- Both the Login form and OTP module use the same `/login` URL.
- The OTP module receives the submitted username, password, and masked email from client-side state.

### OTP Module (Verify Login)

#### 4. OTP Screen

The OTP module displays:

- The masked email address.
- A timer starting at 110 seconds when the module renders.
- The number of remaining OTP verification attempts.
- Six separate OTP input boxes, one per digit.
- A Resend OTP button.

The OTP module does not have a separate URL.

#### 5. OTP Submission

When all six OTP boxes are filled, the client automatically submits the OTP and username to the `/auth/verify-login` endpoint.

The OTP input supports numeric entry, automatic focus movement, backspace navigation, and pasted codes.

#### 6. Timer Behavior

- The timer starts at 110 seconds and counts down.
- The Resend OTP button remains disabled while the timer is running.
- When the timer reaches zero, the OTP input boxes are disabled.
- When the timer reaches zero, the Resend OTP button becomes enabled.
- Timer expiry does not redirect the user to the Login form because the user can resend the OTP.

#### 7. Attempt Behavior

- The client displays three remaining verification attempts when the OTP module renders.
- Each failed `/auth/verify-login` response with status `401` reduces the remaining attempts by one.
- The OTP boxes are cleared and focused again after an incorrect OTP.
- When the remaining attempts reach zero, the client returns the user to the Login form.

#### 8. Resend OTP Behavior

When the timer has expired and the user clicks Resend OTP:

- The client calls `/auth/login` again using the username and password stored in client-side state.
- The existing OTP is replaced by the backend.
- The masked email is updated if the response contains a new value.
- The timer restarts at 110 seconds.
- The remaining attempts reset to three.
- The OTP boxes are cleared.
- The Resend OTP button becomes disabled again while the new timer runs.

If resending fails, the error is displayed and the Resend OTP button remains available.

#### 9. Successful OTP Verification

When `/auth/verify-login` returns successfully:

- The access token is stored in the global authentication Context.
- The refresh token is stored in the browser's cookie jar by the backend.
- The user is navigated to the `/dashboard` route.

### Dashboard Page

#### 10. Protected Dashboard Route

The `/dashboard` route is a protected route.

- If the access token is not present in the global authentication Context, the user is redirected to the `/login` page.
- If the access token is present, the user can access the dashboard.

#### 11. Fetching Patients Data

When the dashboard page renders, it initially calls the `GET /patients` endpoint to retrieve the patients' data.

The authentication flow works as follows:

- If the access token is expired, the `POST /auth/refresh` endpoint is called to obtain a fresh access token.
- If the `POST /auth/refresh` endpoint returns a `401 Unauthorized` response, it indicates that the refresh token is invalid or expired. The user's session is considered expired, and the user is redirected to the `/login` page.
- If the access token is valid or the `POST /auth/refresh` endpoint successfully returns a fresh access token, the `GET /patients` endpoint returns the patients' data in the form of an array.
- If patients exist, their data is rendered on the dashboard UI.

#### 12. Logout Functionality

The dashboard provides a logout functionality.

When the user clicks the logout button:

- The access token is cleared from the global authentication Context after the server confirms logout.
- The refresh token is cleared from the browser's cookie jar.
- The user is redirected to the `/login` page.

#### 13. Logout From All Devices

The dashboard also provides a logout-from-all-devices functionality.

When the user clicks the logout-from-all-devices button, the user's account is logged out from all other devices and tabs where the account is currently authenticated.

#### 14. Add Patient Functionality

The dashboard provides an Add Patient button.

- When the user clicks the Add Patient button, a popup appears.
- The user enters the patient's information in the popup.
- When the user clicks the Add button inside the popup, the `POST /patients` endpoint is called.
- The patient is added to the system.

Note: For any backend-protected endpoint that requires JWT token validation, if the JWT access token validation fails when the endpoint is called from the client side, the client must call the `POST /auth/refresh` endpoint to obtain a new access token. A successful refresh updates the global authentication Context with the new access token. If the refresh token is expired or invalid, the client must redirect the user to the `/login` page, clear the refresh token from the cookie jar, and clear the access token from the global authentication Context.

## Project Development Approach

I develop the React project page-by-page and module-by-module. I first complete one page or module before moving on to the next.

For each page or module, I follow this approach:

1. **UI Development:** First, develop and complete the UI of the page or module.
2. **Backend Integration:** Once the UI is completed, connect the page or module to its specific backend API endpoints.
3. **Response and Error Handling:** Handle the API responses, server-side exceptions, errors, and behaviors appropriately within the client-side architecture and UI.

### Development Sequence

For example, in the Patients Management System using JWT Two-Factor Authentication, I first develop the Authentication module, then the OTP module, followed by the Dashboard page. After completing the Dashboard UI, I implement and integrate its functionalities, such as adding patients, logging out, and logging out from all devices.

Follow this development approach consistently throughout the project.

## Frontend Folder Structure (My React project folder structure)

All project code is located inside the src directory.

1. Components

The Components folder contains components that are shared across the project.

A component belongs to this folder if it is used by at least two or more pages/modules. The shared authentication UI components (`AuthLayout`, `AuthHeader`, `AuthAlert`, `AuthInput`, and `AuthButton`) belong here because both the Authentication and OTP modules use them. The global `AuthProvider` and `AuthLoadingScreen` components also belong here because the application shell and route guards use them.

2. Utils

The Utils folder contains utility functions that are shared across the project.

A utility function belongs to this folder if it is used by at least two or more pages/modules. The shared `authApi` utility belongs here because both the Authentication and OTP modules call authentication endpoints. The `authTokenStore` in-memory token bridge and the `authContext` context definition also belong here because both React components and the non-React API client use them.

3. Configuration

The Configuration folder contains configurations for external services used in the project, such as Firebase and backend configuration.

4. Hooks

The Hooks folder contains custom hooks that are shared across the project.

A hook belongs to this folder if it is used by at least two or more pages/modules. The shared `useAuthContext` hook belongs here because the Login page, Logout menu, and route guards use it.

5. Project Page/Module Folders

Each page/module has its own dedicated folder containing:

Main file (like Dashboard.jsx)

-> components

-> hooks

-> utils

The components, hooks, and utils folders inside a specific page/module contain only the components, hooks, and utility functions that belong to that page/module.

If a component, hook, or utility function is initially used within a specific page/module but is later shared by another page/module, it must be moved to the corresponding global Components, Hooks, or Utils folder.

These page/module folders are not limited to a single folder. The project can contain multiple such folders.

Example: Current Project Structure

The Authentication, OTP, and Dashboard modules are examples of page/module folders. Each has its own main file, components, hooks, and utils as needed.

Since the project currently contains these modules, any components, hooks, or utility functions shared between them must be placed in the global Components, Hooks, or Utils folders.

The objective is to keep module-specific code within its respective module folder and shared code within the corresponding global folder.
