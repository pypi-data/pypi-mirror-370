from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

import next_cvat

from ..settings import settings


def create_token(
    interactive: bool = typer.Option(
        False, "--interactive", "-i", help="Prompt for credentials interactively"
    ),
    env_file: Optional[Path] = typer.Option(
        None,
        "--env-file",
        "-f",
        help="Load credentials from a specific .env file",
    ),
    use_env: bool = typer.Option(
        False,
        "--env",
        "-e",
        help="Force using environment variables instead of env file",
    ),
):
    """
    Create an authentication token for CVAT.

    Can be run using either 'next-cvat create-token' or 'cvat create-token'.

    Authentication methods (in order of precedence):
    1. Interactive prompt (if --interactive flag is set)
    2. Environment variables (if --env flag is set)
    3. Specified environment file (if --env-file is set)
    4. Default environment file (.env.cvat.secrets)
    5. Falls back to interactive prompt only if no flags are set

    The command will fail if:
    - --env is set but no environment variables are found
    - --env-file is set but no credentials are found in the file

    Examples:
        cvat create-token --interactive
        cvat create-token --env  # use only environment variables
        cvat create-token --env-file .env.custom
        cvat create-token  # uses .env.cvat.secrets or env vars, falls back to interactive
    """
    if interactive:
        username = typer.prompt("Enter your CVAT username")
        password = typer.prompt("Enter your CVAT password", hide_input=True)
    else:
        if env_file is None and not use_env:
            env_file = ".env.cvat.secrets"

        settings_ = settings(env_file=env_file)

        no_credentials = not settings_.username or not settings_.password

        if no_credentials:
            if use_env:
                typer.echo("No credentials found in environment variables.", err=True)
                raise typer.Exit(1)
            elif env_file:
                typer.echo(f"No credentials found in {env_file}.", err=True)
                raise typer.Exit(1)
            else:
                typer.echo(
                    "No credentials found in environment, switching to interactive mode."
                )
                username = typer.prompt("Enter your CVAT username")
                password = typer.prompt("Enter your CVAT password", hide_input=True)
        else:
            username = settings_.username
            password = settings_.password

    token = next_cvat.Client(username=username, password=password).create_token()

    encoded_token = token.serialize()
    print(f"Your machine token is:\n{encoded_token}\n")
    print(f"It expires at {token.expires_at}.")
    return encoded_token
