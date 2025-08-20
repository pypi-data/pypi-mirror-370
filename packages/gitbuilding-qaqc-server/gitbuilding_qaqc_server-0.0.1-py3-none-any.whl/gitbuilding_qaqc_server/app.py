"""A FastAPI server application for GitBuilding QAQC."""
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Optional, Annotated, Any, cast
import os
from datetime import datetime
import asyncio

from fastapi import FastAPI, APIRouter, Depends, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from gitbuilding_qaqc_server import qaqc_db

THIS_DIR = os.path.dirname(__file__)

templates = Jinja2Templates(directory=os.path.join(THIS_DIR, "templates"))
router = APIRouter()


def create_app(db_dir: Optional[str] = None) -> FastAPI:
    """Create application and database if it doesn't exist."""
    if db_dir is None:
        db_dir = "./database"
    # Ensure the database directory exists
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, "qaqc-data.sqlite")

    # Create tables at startup if they don't exist. Use asyncio run so we can always
    # use the same async sqlite library rather than switching to a non-async library
    # for setup
    asyncio.run(qaqc_db.create_database(db_path))

    app = FastAPI()
    app.state.db_path = db_path

    # Mount static files
    app.mount(
        "/static",
        StaticFiles(directory=os.path.join(THIS_DIR, "static")),
        name="static",
    )
    app.include_router(router)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
    return app


def get_db(request: Request) -> str:
    """Get the database path. This is designed to be used as a dependency."""
    return cast(str, request.app.state.db_path)


@router.get("/")
async def index_response(request: Request) -> Response:
    """Return a basic index page."""
    return templates.TemplateResponse(
        request, "index.html.jinja", {"current_year": datetime.now().year}
    )


@router.post("/register/{uuid}")
async def register(
    uuid: str,
    registration_data: dict[str, Any],
    request: Request,
    db_path: Annotated[str, Depends(get_db)],
) -> dict[str, str]:
    """Accept submitted data and enter into submissions database."""
    if uuid != registration_data.get("unique-build-id"):
        raise HTTPException(
            status_code=400, detail="Submitted unique-build-id does not match the URL."
        )
    try:
        device_id = await qaqc_db.register_build(registration_data, db_path)
    except (ValueError, TypeError) as e:
        raise HTTPException(400, detail=str(e)) from e
    report_path = request.app.url_path_for("report", device_id=device_id)
    # Return full url with the base prepended:
    report_url = str(request.base_url)[:-1] + report_path
    return {"device-id": device_id, "report-url": report_url}


@router.post("/submit/{uuid}")
async def submit(
    uuid: str, submission: dict[str, Any], db_path: Annotated[str, Depends(get_db)]
) -> None:
    """Accept submitted data and enter into submissions database."""
    if uuid != submission.get("unique-build-id"):
        raise HTTPException(
            status_code=400, detail="Submitted unique-build-id does not match the URL."
        )
    try:
        await qaqc_db.insert_submission(submission, db_path)
    except (ValueError, TypeError, qaqc_db.CannotSubmitError) as e:
        raise HTTPException(400, detail=str(e)) from e


@router.get("/report/{device_id}")
async def report(
    device_id: str, request: Request, db_path: Annotated[str, Depends(get_db)]
) -> Response:
    """Generate and return HTML report for the build with the input device ID.

    This page will eventually contain human readable information but does not yet.
    """
    title, expected_submissions, submissions = await qaqc_db.get_data_for_report(
        device_id, db_path
    )

    submitted_ids = [sub["form_id"] for sub in submissions]
    expected_ids = [sub["form_id"] for sub in expected_submissions]
    complete = set(expected_ids) == set(submitted_ids)

    report_path = request.app.url_path_for("report_json", device_id=device_id)
    # Return full url with the base prepended:
    report_url = str(request.base_url)[:-1] + report_path

    return templates.TemplateResponse(
        request,
        "report.html.jinja",
        {
            "device_id": device_id,
            "device_title": title,
            "complete": complete,
            "report_url": report_url,
        },
    )


@router.get("/report_json/{device_id}")
async def report_json(
    device_id: str, db_path: Annotated[str, Depends(get_db)]
) -> list[dict[str, Any]]:
    """Return JSON data for all QAQC submissions for this device ID."""
    _title, _expected_submissions, submissions = await qaqc_db.get_data_for_report(
        device_id, db_path
    )
    return submissions
