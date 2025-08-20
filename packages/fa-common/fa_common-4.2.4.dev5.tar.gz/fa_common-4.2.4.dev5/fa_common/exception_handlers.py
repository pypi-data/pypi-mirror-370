import traceback
from typing import Any

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request

from fa_common.exceptions import RuleValidationError

from .config import get_settings
from .responses import ORJSONResponse
from .utils import logger as LOG


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> ORJSONResponse:
    """
    Handles StarletteHTTPException, translating it into flat dict error data:
        * code - unique code of the error in the system
        * detail - general description of the error
        * fields - list of dicts with description of the error in each field.

    :param request: Starlette Request instance
    :param exc: StarletteHTTPException instance
    :return: ORJSONResponse with newly formatted error data
    """
    fields = getattr(exc, "fields", [])
    data = {
        "code": getattr(exc, "code", "Error"),
        "detail": getattr(exc, "message", exc.detail),
        "fields": fields,
    }
    return ORJSONResponse(data, status_code=exc.status_code)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> ORJSONResponse:
    """
    Handles ValidationError, translating it into flat dict error data:
        * code - unique code of the error in the system
        * detail - general description of the error
        * fields - list of dicts with description of the error in each field.

    :param request: Starlette Request instance
    :param exc: StarletteHTTPException instance
    :return: ORJSONResponse with newly formatted error data
    """
    if get_settings().ROLLBAR_KEY is not None:
        import rollbar

        rollbar.report_message(f"RequestValidationError Caught: {exc}", "warning")

    LOG.warning(f"RequestValidationError Caught: {exc}")
    status_code = getattr(exc, "status_code", 422)
    errors: list[dict[str, Any]] = []
    details = str(exc)
    try:
        errors.extend(
            {
                "area": error.get("loc", ("", ""))[0],
                "variable": error.get("loc", ("", ""))[1] if len(error.get("loc", ("", ""))) > 1 else "",
                "message": error.get("msg"),
                "type": error.get("type"),
            }
            for error in exc.errors()
        )
        details = "One or more fields has failed validation."
    except Exception as err:
        LOG.error(f"Problem creating validation error response. {err}")
    # FIXME make validation errors better
    data = {"code": "Validation Error", "detail": details, "errors": errors}
    return ORJSONResponse(data, status_code=status_code)


async def pydantic_validation_exception_handler(request: Request, exc: ValidationError) -> ORJSONResponse:
    """
    Handles ValidationError, translating it into flat dict error data:
        * code - unique code of the error in the system
        * detail - general description of the error
        * fields - list of dicts with description of the error in each field.

    :param request: Starlette Request instance
    :param exc: StarletteHTTPException instance
    :return: ORJSONResponse with newly formatted error data
    """
    if get_settings().ROLLBAR_KEY is not None:
        import rollbar

        rollbar.report_exc_info()

    LOG.error(f"Unhandled Pydantic ValidationError Caught: {exc!s}")
    # errors = []
    # try:
    #     for error in exc.errors():
    #         errors.append(
    #             {
    #                 "area": error.get("loc", ("", ""))[0],
    #                 "variable": error.get("loc", ("", ""))[1],
    #                 "message": error.get("msg"),
    #                 "type": error.get("type"),
    #             }
    #         )
    # except Exception as err:
    #     LOG.error(f"Problem creating validation error response. {err}")

    data = {
        "code": "Server Validation Error",
        "detail": "A domain object has failed validation this is likely due to changes in the model or "
        + "database structure. Creating a new dataset may solve the issue.",
        "error": str(exc),
    }
    return ORJSONResponse(data, status_code=500)


async def assert_exception(request: Request, exc: AssertionError) -> ORJSONResponse:
    if get_settings().ROLLBAR_KEY is not None:
        import rollbar

        rollbar.report_message(f"Assert exception caught: {exc!s}", "warning")

    LOG.warning(f"Assert exception caught: {exc!s}")
    data = {"code": "Assertion Error", "detail": str(exc)}
    return ORJSONResponse(data, status_code=400, headers={"Access-Control-Allow-Origin": "*"})


async def rule_exception(request: Request, exc: RuleValidationError) -> ORJSONResponse:
    if get_settings().ROLLBAR_KEY is not None:
        import rollbar

        rollbar.report_message(f"Rule Validation error caught: {exc!s}", "warning")

    LOG.warning(f"Rule Validation caught: {exc!s}")
    data = {"code": "Rule Validation Error", "detail": str(exc)}
    return ORJSONResponse(data, status_code=400, headers={"Access-Control-Allow-Origin": "*"})


async def default_exception(request: Request, exc: Exception) -> ORJSONResponse:
    if get_settings().ROLLBAR_KEY is not None:
        import rollbar

        rollbar.report_exc_info()
    LOG.error(f"Internal exception caught: {exc}")
    data = {
        "code": "Internal Server Error",
        "detail": str(exc),
        "trace": traceback.format_exc(),
    }

    return ORJSONResponse(data, status_code=500, headers={"Access-Control-Allow-Origin": "*"})


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Helper function to setup exception handlers for app.
    Use during app startup as follows:

    .. code-block:: python

        app = FastAPI()

        @app.on_event('startup')
        async def startup():
            setup_exception_handlers(app)

    :param app: app object, instance of FastAPI
    :return: None
    """
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)
    app.add_exception_handler(AssertionError, assert_exception)
    app.add_exception_handler(RuleValidationError, rule_exception)
    app.add_exception_handler(Exception, default_exception)
