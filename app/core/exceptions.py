"""Domain exceptions mapped to HTTP responses at the API boundary."""


class DomainError(Exception):
    """Base exception for expected business-rule violations."""

    status_code = 400
    detail = "A domain error occurred."

    def __init__(self, detail: str | None = None) -> None:
        self.detail = detail or self.detail
        super().__init__(self.detail)


class UnauthorizedError(DomainError):
    """Base class for authentication failures."""

    status_code = 401
    detail = "Authentication is required."


class ForbiddenError(DomainError):
    """Base class for authorization failures."""

    status_code = 403
    detail = "Access is forbidden."


class NotFoundError(DomainError):
    """Base class for missing resources."""

    status_code = 404
    detail = "Resource was not found."


class ConflictError(DomainError):
    """Raised when a request conflicts with the current state of the resource."""

    status_code = 409
    detail = "Resource conflict."


class UserAlreadyExistsError(ConflictError):
    """Raised when an email address or username is already registered."""

    detail = "A user with these details already exists."


class InvalidCredentialsError(UnauthorizedError):
    """Raised when supplied authentication credentials are invalid."""

    detail = "Invalid email or password."


class AuthenticationRequiredError(UnauthorizedError):
    """Raised when a protected resource is accessed without valid authentication."""

    detail = "Authentication is required."


class UserNotFoundError(NotFoundError):
    """Raised when an expected user no longer exists."""

    detail = "User was not found."


class ProjectNotFoundError(NotFoundError):
    """Raised when a requested project does not exist."""

    detail = "Project was not found."


class ProjectAccessDeniedError(ForbiddenError):
    """Raised when a user tries to access a project they do not own."""

    detail = "You do not have access to this project."


class TaskNotFoundError(NotFoundError):
    """Raised when a requested task does not exist."""

    detail = "Task was not found."


class MemberNotFoundError(NotFoundError):
    """Raised when a project member is not found."""

    detail = "Member was not found."


class MemberAlreadyExistsError(ConflictError):
    """Raised when a user is already a member of a project."""

    detail = "User is already a member of this project."


class InsufficientPermissionError(ForbiddenError):
    """Raised when a user lacks the required role level for an action."""

    detail = "You do not have sufficient permissions for this action."
