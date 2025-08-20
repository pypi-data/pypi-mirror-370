from typing import Any, Dict, List

from starlette.exceptions import HTTPException as StarletteHTTPException


class DatabaseError(Exception):
    """
    Simple exception to notify something unexpected has happened with a
    database call.
    """


class JobExecutionError(Exception):
    """
    Simple exception to notify something unexpected has happened with a
    job execution in a workflow run.
    """


class StorageError(Exception):
    """
    Simple exception to notify something unexpected has happened with a
    storage call.
    """


class RuleValidationError(Exception):
    """Simple exception to capture an application business rule that has failed."""


class HTTPException(StarletteHTTPException):
    """Generic HTTP Exception with support for custom status & error codes."""

    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        error_name: str = "Http Error",
        fields: List[Dict] | None = None,
    ) -> None:
        """
        Generic HTTP Exception with support for custom status & error codes.

        :param status_code: HTTP status code of the response
        :param error_code: Custom error code, unique throughout the app
        :param detail: detailed message of the error
        :param fields: list of dicts with key as field and value as message
        """
        super().__init__(status_code=status_code, detail=detail)
        self.code = error_name
        self.fields = fields or []


class InternalServerError(HTTPException):
    def __init__(self, detail: Any, fields: List[Dict] | None = None):
        """
        Generic Internal Server error.

        :param detail: detailed message of the error
        """
        super().__init__(
            error_name="Internal Server Error",
            status_code=500,
            detail=detail,
            fields=fields,
        )


class UnImplementedError(HTTPException):  #
    def __init__(self, detail: Any, fields: List[Dict] | None = None):
        """
        Generic Unimplemented error.

        :param detail: detailed message of the error
        """
        super().__init__(
            error_name="Not Implemented Error",
            status_code=501,
            detail=detail,
            fields=fields,
        )


class UnknownError(HTTPException):
    def __init__(self, detail: Any, fields: List[Dict] | None = None):
        """
        Generic Unknown error that has been explicitly caught, uses "BadRequest" status code.

        :param detail: detailed message of the error
        """
        super().__init__(
            error_name="Unknown Error",
            status_code=400,
            detail=detail,
            fields=fields,
        )


class BadRequestError(HTTPException):
    def __init__(self, detail: Any, fields: List[Dict] | None = None):
        """
        Generic Bad Request HTTP Exception with support for custom error code.

        :param error_code: Custom error code, unique throughout the app
        :param detail: detailed message of the error
        """
        super().__init__(
            error_name="Bad Request Error",
            status_code=400,
            detail=detail,
            fields=fields,
        )


class UnauthorizedError(HTTPException):
    """Generic Unauthorized HTTP Exception with support for custom error code."""

    def __init__(
        self,
        detail: Any = "Unauthorized",
        fields: List[Dict] | None = None,
    ):
        """
        Generic Unauthorized HTTP Exception with support for custom error code.

        :param error_code: Custom error code, unique throughout the app
        :param detail: detailed message of the error
        """
        super().__init__(
            error_name="Unauthorised Error",
            status_code=401,
            detail=detail,
            fields=fields,
        )


class ForbiddenError(HTTPException):
    """Generic Forbidden HTTP Exception with support for custom error code."""

    def __init__(
        self,
        detail: Any = "Forbidden.",
        fields: List[Dict] | None = None,
    ):
        """
        Generic Forbidden HTTP Exception with support for custom error code.

        :param error_code: Custom error code, unique throughout the app
        :param detail: detailed message of the error
        """
        super().__init__(
            error_name="Forbidden Error",
            status_code=403,
            detail=detail,
            fields=fields,
        )


class NotFoundError(HTTPException):
    """Generic 404 Not Found HTTP Exception with support for custom error code."""

    def __init__(
        self,
        detail: Any = "Not found.",
        fields: List[Dict] | None = None,
    ):
        """
        Generic 404 Not Found HTTP Exception with support for custom error code.

        :param error_code: Custom error code, unique throughout the app
        :param detail: detailed message of the error
        """
        super().__init__(
            error_name="Not Found Error",
            status_code=404,
            detail=detail,
            fields=fields,
        )


class AlreadyExistsError(HTTPException):
    """409 Conflict HTTP Exception with support for custom error code."""

    def __init__(
        self,
        detail: Any = "Already Exists.",
        fields: List[Dict] | None = None,
    ):
        """
        409 Conflict HTTP Exception with support for custom error code.

        :param error_code: Custom error code, unique throughout the app
        :param detail: detailed message of the error
        """
        super().__init__(
            error_name="Already Exists Error",
            status_code=409,
            detail=detail,
            fields=fields,
        )
