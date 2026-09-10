# Error Responses Documentation

This document describes all possible HTTP error responses from the ProjectHub API.

## Authentication & Authorization Errors

### 401 Unauthorized - Invalid Credentials
```json
{
  "detail": "Invalid email or password."
}
```
**When:** User provides wrong credentials during login.
**Status Code:** 401
**Exception:** `InvalidCredentialsError`

### 401 Unauthorized - Authentication Required
```json
{
  "detail": "Authentication is required."
}
```
**When:** Protected endpoint accessed without valid JWT token.
**Status Code:** 401
**Exception:** `AuthenticationRequiredError`

### 403 Forbidden - Access Denied
```json
{
  "detail": "You do not have access to this project."
}
```
**When:** User tries to access/modify a project they don't own.
**Status Code:** 403
**Exception:** `ProjectAccessDeniedError`

### 403 Forbidden - Insufficient Permissions
```json
{
  "detail": "You do not have sufficient permissions for this action."
}
```
**When:** User lacks required role (ADMIN, OWNER) for an action.
**Status Code:** 403
**Exception:** `InsufficientPermissionError`

## Resource Not Found Errors

### 404 Not Found - Project
```json
{
  "detail": "Project was not found."
}
```
**When:** Requested project doesn't exist.
**Status Code:** 404
**Exception:** `ProjectNotFoundError`
**Endpoints:** GET/PATCH/DELETE `/api/v1/projects/{id}`, GET/POST `/api/v1/projects/{id}/tasks`, GET/POST/PATCH/DELETE `/api/v1/projects/{id}/members`

### 404 Not Found - Task
```json
{
  "detail": "Task was not found."
}
```
**When:** Requested task doesn't exist.
**Status Code:** 404
**Exception:** `TaskNotFoundError`
**Endpoints:** GET/PATCH/DELETE `/api/v1/tasks/{id}`

### 404 Not Found - User
```json
{
  "detail": "User was not found."
}
```
**When:** Requested user doesn't exist.
**Status Code:** 404
**Exception:** `UserNotFoundError`

### 404 Not Found - Member
```json
{
  "detail": "Member was not found."
}
```
**When:** Project member doesn't exist.
**Status Code:** 404
**Exception:** `MemberNotFoundError`
**Endpoints:** PATCH/DELETE `/api/v1/projects/{id}/members/{user_id}`

## Conflict Errors

### 409 Conflict - User Already Exists
```json
{
  "detail": "A user with these details already exists."
}
```
**When:** Email or username already registered.
**Status Code:** 409
**Exception:** `UserAlreadyExistsError`
**Endpoints:** POST `/api/v1/auth/register`

### 409 Conflict - Member Already Exists
```json
{
  "detail": "User is already a member of this project."
}
```
**When:** Trying to add a user who's already a project member.
**Status Code:** 409
**Exception:** `MemberAlreadyExistsError`
**Endpoints:** POST `/api/v1/projects/{id}/members`

## Validation Errors

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "name"],
      "msg": "String should have at least 1 character",
      "input": ""
    }
  ]
}
```
**When:** Request body fails Pydantic validation.
**Common Cases:**
- Empty required fields
- Invalid email format
- Password too short (< 12 characters)
- Invalid UUID format
- Invalid enum values (status, priority, role)
- Page or page_size out of valid range

## Server Errors

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```
**When:** Unexpected server-side error occurred.
**Status Code:** 500

## Error Response Structure

All error responses follow this format:

```json
{
  "detail": "Error message or array of validation errors"
}
```

For validation errors (422), `detail` is an array of objects with structure:
```json
{
  "type": "error_type",
  "loc": ["location", "path"],
  "msg": "Human readable message",
  "input": "provided value"
}
```

## Common Error Scenarios by Endpoint

### Authentication Endpoints
- **POST /api/v1/auth/register**
  - 422: Validation error (invalid email, short password, empty username)
  - 409: Email or username already exists

- **POST /api/v1/auth/login**
  - 422: Validation error (invalid email format)
  - 401: Invalid credentials

- **POST /api/v1/auth/refresh**
  - 401: Invalid or expired refresh token

### Project Endpoints
- **GET /api/v1/projects**
  - 401: Not authenticated
  - 422: Invalid pagination parameters

- **POST /api/v1/projects**
  - 401: Not authenticated
  - 422: Validation error (empty name, name too long)

- **GET /api/v1/projects/{id}**
  - 401: Not authenticated
  - 403: Access denied (not owner)
  - 404: Project not found

- **PATCH /api/v1/projects/{id}**
  - 401: Not authenticated
  - 403: Access denied (not owner)
  - 404: Project not found
  - 422: Validation error

- **DELETE /api/v1/projects/{id}**
  - 401: Not authenticated
  - 403: Access denied (not owner)
  - 404: Project not found

### Task Endpoints
- **GET /api/v1/projects/{id}/tasks**
  - 401: Not authenticated
  - 403: No access to project
  - 404: Project not found

- **POST /api/v1/projects/{id}/tasks**
  - 401: Not authenticated
  - 403: Insufficient permissions (not ADMIN/OWNER)
  - 404: Project not found
  - 422: Validation error

- **GET /api/v1/tasks/{id}**
  - 401: Not authenticated
  - 404: Task not found

- **PATCH /api/v1/tasks/{id}**
  - 401: Not authenticated
  - 404: Task not found
  - 422: Validation error

- **DELETE /api/v1/tasks/{id}**
  - 401: Not authenticated
  - 403: Insufficient permissions
  - 404: Task not found

### Member Endpoints
- **GET /api/v1/projects/{id}/members**
  - 401: Not authenticated
  - 403: No access to project
  - 404: Project not found

- **POST /api/v1/projects/{id}/members**
  - 401: Not authenticated
  - 403: Insufficient permissions (not ADMIN/OWNER)
  - 404: Project not found
  - 409: User already a member
  - 422: Validation error

- **PATCH /api/v1/projects/{id}/members/{user_id}**
  - 401: Not authenticated
  - 403: Insufficient permissions (not OWNER)
  - 404: Project or member not found
  - 422: Validation error

- **DELETE /api/v1/projects/{id}/members/{user_id}**
  - 401: Not authenticated
  - 403: Insufficient permissions (not OWNER)
  - 404: Project or member not found
