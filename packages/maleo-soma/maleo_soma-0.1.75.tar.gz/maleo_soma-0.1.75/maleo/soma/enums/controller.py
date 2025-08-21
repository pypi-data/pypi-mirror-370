from enum import StrEnum
from fastapi import responses


class ServiceController(StrEnum):
    REST = "rest"
    MESSAGE = "message"


class ClientController(StrEnum):
    HTTP = "http"


class RESTControllerResponse(StrEnum):
    NONE = "none"
    HTML = "html"
    TEXT = "text"
    JSON = "json"
    REDIRECT = "redirect"
    STREAMING = "streaming"
    FILE = "file"

    def get_response_type(self) -> type[responses.Response]:
        """Returns the corresponding FastAPI Response type."""
        return {
            RESTControllerResponse.NONE: responses.Response,
            RESTControllerResponse.HTML: responses.HTMLResponse,
            RESTControllerResponse.TEXT: responses.PlainTextResponse,
            RESTControllerResponse.JSON: responses.JSONResponse,
            RESTControllerResponse.REDIRECT: responses.RedirectResponse,
            RESTControllerResponse.STREAMING: responses.StreamingResponse,
            RESTControllerResponse.FILE: responses.FileResponse,
        }.get(self, responses.Response)
