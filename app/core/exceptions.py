"""Domain exceptions mapped to HTTP responses at the API boundary."""


class DomainError(Exception):
    """Base exception for expected business-rule violations."""

    status_code = 400
    detail = "A domain error occurred."

    def __init__(self, detail: str | None = None) -> None:
        self.detail = detail or self.detail
        super().__init__(self.detail)


class ConflictError(DomainError):
    """Raised when a request conflicts with the current state of the resource."""

    status_code = 409
    detail = "Resource conflict."


class UserAlreadyExistsError(ConflictError):
    """Raised when an email address or username is already registered."""

    detail = "A user with these details already exists."


class InvalidCredentialsError(DomainError):
    """Raised when supplied authentication credentials are invalid."""

    status_code = 401
    detail = "Invalid email or password."


class AuthenticationRequiredError(DomainError):
    """Raised when a protected resource is accessed without valid authentication."""

    status_code = 401
    detail = "Authentication is required."


class UserNotFoundError(DomainError):
    """Raised when an expected user no longer exists."""

    status_code = 404
    detail = "User was not found."


class ProjectNotFoundError(DomainError):
    """Raised when a requested project does not exist."""

    status_code = 404
    detail = "Project was not found."


class ProjectAccessDeniedError(DomainError):
    """Raised when a user tries to access a project they do not own."""

    status_code = 403
    detail = "You do not have access to this project."


class TaskNotFoundError(DomainError):
    """Raised when a requested task does not exist."""

    status_code = 404
    detail = "Task was not found."


class MemberNotFoundError(DomainError):
    """Raised when a project member is not found."""

    status_code = 404
    detail = "Member was not found."


class MemberAlreadyExistsError(DomainError):
    """Raised when a user is already a member of a project."""

    status_code = 409
    detail = "User is already a member of this project."


class InsufficientPermissionError(DomainError):
    """Raised when a user lacks the required role level for an action."""

    status_code = 403
    detail = "You do not have sufficient permissions for this action."
