from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from starlette.templating import _TemplateResponse

from .. import __version__ as version
from .. import GFP_DOWEB_HTTPS

router = APIRouter()
templates = Jinja2Templates(
    directory=(Path(__file__).parent.parent / "templates").resolve()
)


class FileView(BaseModel):
    file: Path
    cell: str | None = None
    layer_props: str | None = None
    rdb: str | None = None


@router.get("/view", response_class=HTMLResponse)
async def file_view_static(
    request: Request, params: Annotated[FileView, Depends()]
) -> _TemplateResponse:
    settings = router.dependencies[0].dependency()  # type: ignore[misc]
    _file = settings.fileslocation / f"{params.file}"

    exists = _file.is_file() and _file.stat().st_mode

    if not exists:
        raise HTTPException(
            status_code=404,
            detail=f'No file found with name "{_file}".'
            " It doesn't exist or is not accessible",
        )

    return await show_file(request, layout_params=params)


async def show_file(request: Request, layout_params: FileView) -> _TemplateResponse:
    root_path = request.scope["root_path"]
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

    if request.url.port is not None:
        url = (
            ws_scheme
            + (request.url.hostname or "localhost")
            + ":"
            + str(request.url.port)
            + root_path
        )
    else:
        url = ws_scheme + (request.url.hostname or "localhost") + root_path

    template_params = {
        "request": request,
        "url": url,
        "ws_scheme": ws_scheme,
        "http_scheme": http_scheme,
    }

    template_params["params"] = layout_params.model_dump(mode="json", exclude_none=True)

    return templates.TemplateResponse(
        "viewer.html",
        template_params,
    )


@router.get("/status")
async def doweb_status() -> dict[str, str | int]:
    return {"server": "doweb", "version": version}
