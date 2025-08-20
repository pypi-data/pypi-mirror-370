"""A submodule for database operations.

The database is SQLite, using aiosqlite for async operation.
"""
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Any, Optional
import json
import uuid

import aiosqlite

from gitbuilding_qaqc_server.utilities import (
    validate_uuid,
    validate_gb_id,
    validate_str,
)

# Note that all sql code blocks start with a `--sql` comment and end with ;
# This allows syntax highlighting with python-string-sql VSCode extension


class CannotSubmitError(RuntimeError):
    """Raised if the data for a QaQc form cannot be submitted due to database state.

    For example if a previous form is incomplete, or if the build ID is wrong.
    """


async def create_database(db_path: str) -> None:
    """Create the database and tables if they don't exist."""
    async with aiosqlite.connect(db_path) as db:
        # Each build gets one entry in the `builds` database.
        await db.execute("""--sql
        CREATE TABLE IF NOT EXISTS builds (
            uuid TEXT PRIMARY KEY,
            device_id TEXT,
            device_title TEXT,
            build_id TEXT,
            full_form_structure TEXT
        );
        """)
        await db.commit()
        # Submissions table is for each QAQC submission from a QAQC block, this means
        # that multiple submissions per build, so the UUID cannot be the primary key
        # instead an auto-incrementing primary key is used.
        # At a later date, it may be more efficient to combine complete builds and
        # store separately.
        await db.execute("""--sql
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid TEXT,
            build_id TEXT,
            page_title TEXT,
            form_id TEXT,
            form_data TEXT
        );
        """)


async def register_build(data: dict[str, Any], db_path: str) -> str:
    """Register a new build in the database.

    :param data: dictionary containing:

        - "unique-build-id": the UUID of the build
        - "device-title": The title for the instruction page that starts the build
        - "instruction-build-id": the build ID
        - "full-form-structure": the full form structure

    :param db_path: path to the SQLite database file

    :return: The device_id, this is used to return reports.

    :raises TypeError: if a data within the dictionary is not typed appropriately.
    :raises ValueError: if a build with the same UUID already exists
    """
    unique_build_id = validate_uuid(data.get("unique-build-id"))
    device_title = validate_str(data.get("device-title"))
    instruction_build_id = validate_gb_id(data.get("instruction-build-id"))
    form_structure_obj = data.get("full-form-structure")
    if not isinstance(form_structure_obj, list):
        raise TypeError(
            f"Submitted form data is a {type(form_structure_obj)} not a list"
        )
    for item in form_structure_obj:
        if not isinstance(item, dict):
            raise TypeError(
                "Submitted form data should be a list of dictionaries. "
                f"It should not contain elements of type {type(item)}"
            )
    form_structure = json.dumps(form_structure_obj)
    device_id = str(uuid.uuid4())

    async with aiosqlite.connect(db_path) as db:
        # First check this UUID hasn't already been registered.
        fetch_sql = "SELECT 1 FROM builds WHERE uuid = ?"
        async with db.execute(fetch_sql, (unique_build_id,)) as cursor:
            if await cursor.fetchone():
                raise ValueError(f"Build with UUID {unique_build_id} already exists.")
        # Then register it
        await db.execute(
            """--sql
            INSERT INTO builds (
                uuid,
                device_id,
                device_title,
                build_id,
                full_form_structure
            ) VALUES (?, ?, ?, ?, ?);
            """,
            (
                unique_build_id,
                device_id,
                device_title,
                instruction_build_id,
                form_structure,
            ),
        )
        await db.commit()
        return device_id


async def insert_submission(submission: dict[str, Any], db_path: str) -> dict[str, str]:
    """Insert a single submission from a QAQc block into the database."""
    # Check the json format is valid
    valid_data = validate_submission(submission)
    # Check the data matches what is expected from the current database state.
    await check_database_for_submission(valid_data, db_path)
    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            """--sql
            INSERT INTO submissions (uuid, build_id, page_title, form_id, form_data)
            VALUES (?, ?, ?, ?, ?);
            """,
            valid_data,
        )
        await db.commit()
    return {"status": "ok"}


def validate_submission(submission: dict[str, Any]) -> tuple[str, str, str, str, str]:
    """Validate submission dictionary and return as tuple for database insertion."""
    unique_build_id = validate_uuid(submission.get("unique-build-id"))
    instruction_build_id = validate_gb_id(submission.get("instruction-build-id"))
    page_title = validate_str(submission.get("page-title"))
    form_id = validate_gb_id(submission.get("form-id"))

    form_data_dict = submission.get("form-data")
    if not isinstance(form_data_dict, dict):
        raise TypeError(f"Submitted form data is a {type(form_data_dict)} not a dict")
    form_data = json.dumps(form_data_dict)

    return unique_build_id, instruction_build_id, page_title, form_id, form_data


async def check_database_for_submission(
    data: tuple[str, str, str, str, str], db_path: str
) -> None:
    """Check that a submission can be inserted into the database.

    This involves checking that:

    * the UUID is registered
    * the previous steps are complete
    * the data is in the correct format.

    :param data: Tuple ready for database insertion: unique_build_id,
        instruction_build_id, page_title, form_id, form_data
    :param db_path: Path to the SQLite database.

    :raises CannotSubmitError: if data cannot be submitted.
    """
    # Unpack tuple.
    unique_build_id, instruction_build_id, _page_title, form_id, _form_data = data

    # First check the builds Table, to check the build is registered.
    build_data = await get_build_by_uuid(unique_build_id, db_path)
    if build_data is None:
        raise CannotSubmitError(f"No build with {unique_build_id} registered")
    if build_data["build_id"] != instruction_build_id:
        raise CannotSubmitError(
            f"For UUID: {unique_build_id} the instruction build id should be "
            f"{build_data['build_id']}"
        )
    expected_submissions = json.loads(build_data["full_form_structure"])

    # Next check submissions
    matched_submissions = await get_submissions_by_uuid(unique_build_id, db_path)

    next_submission = determine_next_submission(
        expected_submissions, matched_submissions
    )
    if form_id != next_submission["form_id"]:
        raise CannotSubmitError(
            f"Form `{form_id}` submitted, expecting form `{next_submission['form_id']}`"
        )


def determine_next_submission(
    expected_submissions: list[dict[str, Any]],
    matched_submissions: list[dict[str, Any]],
) -> dict[str, Any]:
    """Determine the next valid submission and error if records are in invalid state.

    :param expected_submissions: The full form data submitted on registration.
    :param matched_submissions:

    :return: The next item from expected sumission

    :raises CannotSubmitError: is data is in invalid state
    """
    # If there are no matched submissions, the next submission is the first expected
    if not matched_submissions:
        return expected_submissions[0]

    n_matches = len(matched_submissions)
    # check the n matched IDs are match the first n expected ids
    submitted_ids = [sub["form_id"] for sub in matched_submissions]
    expected_ids = [sub["form_id"] for sub in expected_submissions[:n_matches]]
    if set(submitted_ids) != set(expected_ids):
        raise CannotSubmitError(
            "Cannot proceed, submitted data for this build is in a broken state!"
        )
    if n_matches == len(expected_submissions):
        raise CannotSubmitError("Cannot proceed form is complete.")

    return expected_submissions[n_matches]


async def get_data_for_report(
    device_id: str, db_path: str
) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
    """Return the data needed for a report.

    :param build_uuid: UUID to look up.
    :param db_path: Path to the SQLite database.

    :returns: Tuple of the device title, expected structure (dictionary) and submitted
        forms (list of dictionaries. Form data is turned into a dict)

    :raises ValueError: The build is not registered at all.
    """
    build_record = await get_build_by_device_id(device_id, db_path)
    if build_record is None:
        raise ValueError("No build record found for ID.")
    build_uuid = build_record["uuid"]
    expected_submissions = json.loads(build_record["full_form_structure"])
    submissions = await get_submissions_by_uuid(build_uuid, db_path)
    for submission in submissions:
        submission["form_data"] = json.loads(submission["form_data"])
    return build_record["device_title"], expected_submissions, submissions


async def get_build_by_uuid(build_uuid: str, db_path: str) -> Optional[dict[str, Any]]:
    """Check if a build with the given UUID exists and return its details.

    :param build_uuid: UUID to look up.
    :param db_path: Path to the SQLite database.

    :return: Dictionary with keys matching the builds table or None if not found.
    """
    query = """--sql
        SELECT *
        FROM builds
        WHERE uuid = ?;
        """
    return await get_single_record(query, (build_uuid,), db_path)


async def get_build_by_device_id(
    device_id: str, db_path: str
) -> Optional[dict[str, Any]]:
    """Check if a build with the given UUID exists and return its details.

    :param device_id: Device ID to look up.
    :param db_path: Path to the SQLite database.

    :return: Dictionary with keys matching the builds table or None if not found.
    """
    query = """--sql
        SELECT *
        FROM builds
        WHERE device_id = ?;
        """
    return await get_single_record(query, (device_id,), db_path)


async def get_single_record(
    query: str, value: tuple[Any], db_path: str
) -> Optional[dict[str, Any]]:
    """Return a single record from a table as a dictionary (or none if missing).

    :param query: The SQL query
    :param value: The value for the query should be a tuple
    :param db_path: Path to the SQLite database.

    :return: Dictionary with keys matching the specified table or None if not found.
    """
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(query, value) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
            return None


async def get_submissions_by_uuid(
    build_uuid: str, db_path: str
) -> list[dict[str, Any]]:
    """Fetch all submissions matching a specific UUID.

    :param build_uuid: UUID to filter submissions.
    :param db_path: Path to the SQLite database.

    :return:  List of dictionaries, each representing a submission row.
    """
    query = """--sql
        SELECT *
        FROM submissions
        WHERE uuid = ?;
        """
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(query, (build_uuid,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
