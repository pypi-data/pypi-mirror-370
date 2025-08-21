import typer

from .create_token import create_token
from .download import download

app = typer.Typer(
    name="next-cvat",
    help="CLI tool for downloading and handling CVAT annotations",
)

app.command()(create_token)
app.command()(download)
