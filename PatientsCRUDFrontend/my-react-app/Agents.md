# Patients Management System using JWT Two-Factor Authentication

## Project Description and Workflow

### Authentication Module (Login,SignUp Page)

#### 1. Root URL and Login Redirection

When a user accesses the root URL (`/`), they are redirected to the `/login` route.

The `/login` route is a public route. However, if an access token is present in the browser's local storage, the user is redirected to the `/dashboard` route.

#### 2. User Login and Signup

If the access token is not present in local storage, the user must log in or sign up.

Upon successful login or signup:

- The access token is stored in the browser's local storage.
- The refresh token is stored in the browser's cookie jar.

### Dashboard Page

#### 3. Protected Dashboard Route

The `/dashboard` route is a protected route.

- If the access token is not present in local storage, the user is redirected to the `/login` page.
- If the access token is present, the user can access the dashboard.

#### 4. Fetching Patients Data

When the dashboard page renders, it initially calls the `GET /patients` endpoint to retrieve the patients' data.

The authentication flow works as follows:

- If the access token is expired, the `POST /refresh` endpoint is called to obtain a fresh access token.
- If the `POST /refresh` endpoint returns a `401 Unauthorized` response, it indicates that the refresh token is invalid or expired. The user's session is considered expired, and the user is redirected to the `/login` page.
- If the access token is valid or the `POST /refresh` endpoint successfully returns a fresh access token, the `GET /patients` endpoint returns the patients' data in the form of an array.
- If patients exist, their data is rendered on the dashboard UI.

#### 5. Logout Functionality

The dashboard provides a logout functionality.

When the user clicks the logout button:

- The access token is deleted from local storage.
- The refresh token is cleared from the browser's cookie jar.
- The user is redirected to the `/login` page.

#### 6. Logout From All Devices

The dashboard also provides a logout-from-all-devices functionality.

When the user clicks the logout-from-all-devices button, the user's account is logged out from all other devices and tabs where the account is currently authenticated.

#### 7. Add Patient Functionality

The dashboard provides an Add Patient button.

- When the user clicks the Add Patient button, a popup appears.
- The user enters the patient's information in the popup.
- When the user clicks the Add button inside the popup, the `POST /patients` endpoint is called.
- The patient is added to the system.

Note: For any backend-protected endpoint that requires JWT token validation, if the JWT access token validation fails when the endpoint is called from the client side, the client must call the `POST /refresh` endpoint to obtain a new access token. If the refresh token is expired or invalid, the client must redirect the user to the `/login` page, clear the refresh token from the cookie jar, and remove the access token from local storage.

## Project Development Approach

I develop the React project page-by-page and module-by-module. I first complete one page or module before moving on to the next.

For each page or module, I follow this approach:

1. **UI Development:** First, develop and complete the UI of the page or module.
2. **Backend Integration:** Once the UI is completed, connect the page or module to its specific backend API endpoints.
3. **Response and Error Handling:** Handle the API responses, server-side exceptions, errors, and behaviors appropriately within the client-side architecture and UI.

### Development Sequence

For example, in the Patients Management System using JWT Two-Factor Authentication, I first develop the Authentication module, followed by the Dashboard page. After completing the Dashboard UI, I implement and integrate its functionalities, such as adding patients, logging out, and logging out from all devices.

Follow this development approach consistently throughout the project.

## Frontend Folder Structure (My reat project folder structure)

All project code is located inside the src directory.

1. Components

The Components folder contains components that are shared across the project.

A component belongs to this folder if it is used by at least two or more pages/modules.

2. Utils

The Utils folder contains utility functions that are shared across the project.

A utility function belongs to this folder if it is used by at least two or more pages/modules.

3. Configuration

The Configuration folder contains configurations for external services used in the project, such as Firebase and backend configuration.

4. Hooks

The Hooks folder contains custom hooks that are shared across the project.

A hook belongs to this folder if it is used by at least two or more pages/modules.

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

The Authentication and Dashboard modules are examples of page/module folders. Each has its own main file, components, hooks, and utils.

Since the project currently contains only two pages/modules — Authentication and Dashboard — any components, hooks, or utility functions shared between these two modules must be placed in the global Components, Hooks, or Utils folders.

The objective is to keep module-specific code within its respective module folder and shared code within the corresponding global folder.
