import os
from shutil import rmtree
from typing import Optional
import calendar
import time

import typer
from pling_publisher.utils import (
    create_zip_file,
    upload,
)

app = typer.Typer()


@app.command()
def publisharchive(
    file: str = os.getcwd(),
    username: Optional[str] = os.environ.get("PLING_USERNAME", None),
    password: Optional[str] = os.environ.get("PLING_PASSWORD", None),
    project_id: Optional[str] = os.environ.get("PLING_PROJECT_ID", None),
):
    file = os.path.abspath(file)

    if upload(username, password, project_id, file):
        typer.echo("Uploaded.")


@app.command()
def publish(
    directory: str = os.getcwd(),
    project_id: Optional[str] = os.environ.get("PLING_PROJECT_ID", None),
    username: Optional[str] = os.environ.get("PLING_USERNAME", None),
    password: Optional[str] = os.environ.get("PLING_PASSWORD", None),
):
    full_zip_path = build(
        directory=directory,
    )

    if upload(username, password, project_id, full_zip_path):
        typer.echo("Uploaded.")


@app.command()
def build(directory: str = os.getcwd()):
    directory = os.path.abspath(directory)

    current_GMT = time.gmtime()

    upload_filename = "archive-" + str(calendar.timegm(current_GMT)) + ".zip"

    dist_directory = os.path.join(directory, "dist")

    if os.path.isdir(dist_directory):
        rmtree(dist_directory)

    os.mkdir(dist_directory)

    full_zip_path = os.path.join(dist_directory, upload_filename)
    create_zip_file(full_zip_path, directory)
    typer.echo(f"Created zip file: {full_zip_path}")
    return full_zip_path
