import typing
import warnings

import orjson
import ujson
from starlette.responses import JSONResponse


class UJSONResponse(JSONResponse):
    """
    Custom Response class, based on default UJSONResponse, but with differences:
        * Allows to have forward slashes inside strings of JSON
        * Limits output to ASCII and escapes all extended characters above 127.

    DEPRECATED: This class is deprecated. Please use ORJSONResponse instead.

    Should be used as `response_class` argument to routes of your app:

    .. code-block:: python

        app = FastAPI()

        @app.get("/", response_class=UJSONResponse)
        async def root():
            return {"a": "b"}
    """

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "UJSONResponse is deprecated. Please use ORJSONResponse instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)

    def render(self, content: typing.Any) -> bytes:
        return ujson.dumps(content, ensure_ascii=True, escape_forward_slashes=False).encode("utf-8")


class ORJSONResponse(JSONResponse):
    media_type = "application/json"

    def render(self, content: typing.Any) -> bytes:
        return orjson.dumps(content, option=orjson.OPT_SERIALIZE_NUMPY)
