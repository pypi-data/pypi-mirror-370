from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

import next_cvat

from ..settings import settings


def download(
    project_id: int = typer.Option(..., "--project-id", help="CVAT project ID"),
    dataset_path: Path = typer.Option(
        ...,
        "--dataset-path",
        help="Path where the dataset will be saved",
        dir_okay=True,
        file_okay=False,
    ),
    env_file: Optional[Path] = typer.Option(
        ".env.cvat.secrets",
        "--env-file",
        "-f",
        help="Load credentials from a specific .env file",
    ),
    include_images: bool = typer.Option(
        True,
        "--include-images",
        help="Include images in the dataset",
    ),
):
    """
    Download annotations and images from a CVAT project.
    """
    settings_ = settings(env_file=env_file)

    next_cvat.Client(
        username=settings_.username,
        password=settings_.password,
        token=settings_.token,
    ).download_(
        project_id=project_id, dataset_path=dataset_path, include_images=include_images
    )
