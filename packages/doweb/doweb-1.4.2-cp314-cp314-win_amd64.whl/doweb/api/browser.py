from itertools import chain
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.templating import _TemplateResponse

from .. import GFP_DOWEB_HTTPS
from ..config import Config

router = APIRouter()
templates = Jinja2Templates(
    directory=(Path(__file__).parent.parent / "templates").resolve()
)


@router.get("/", response_class=HTMLResponse)
async def file_browser(
    request: Request,
) -> _TemplateResponse:
    settings: Config = router.dependencies[0].dependency()  # type: ignore[misc]
    files = chain(
        settings.fileslocation.glob("**/*.gds"), settings.fileslocation.glob("**/*.oas")
    )
    if GFP_DOWEB_HTTPS:
        https = True
    elif request.url.scheme == "https":
        https = True
    elif request.url.scheme == "http":
        https = False
    else:
        raise HTTPException(
            status_code=406, detail=f"Unknown scheme {request.url.scheme}"
        )

    ws_scheme = "wss://" if https else "ws://"
    http_scheme = "https://" if https else "http://"
    return templates.TemplateResponse(
        "browser.html",
        {
            "request": request,
            "folder_files": [
                file.relative_to(settings.fileslocation) for file in files
            ],
            "page_name": f"File Browser    Root: {settings.fileslocation}",
            "root": settings.fileslocation,
            "ws_scheme": ws_scheme,
            "http_scheme": http_scheme,
        },
    )
