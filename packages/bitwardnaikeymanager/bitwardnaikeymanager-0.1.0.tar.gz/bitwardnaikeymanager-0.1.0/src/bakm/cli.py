import typer
from typing_extensions import Annotated
import os

from .core import sync_to_bitwarden, pull_from_bitwarden
from .bitwarden import BitwardenCLI

app = typer.Typer(
    name="bakm",
    help="A CLI tool to manage AI model configurations and sync them with Bitwarden.",
    add_completion=False,
)

@app.callback()
def callback():
    """
    Bitwarden AI Key Manager
    """
    # Check CLI status before running any command
    bw = BitwardenCLI()
    if not bw.is_logged_in():
        typer.secho(
            "Error: Not logged into Bitwarden CLI. Please run `bw login`.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)
    # Check if the vault is locked
    status = bw._run_command(["bw", "status"])
    if status and status.get("status") == "locked":
        typer.secho(
            "Error: Bitwarden vault is locked. Please run `bw unlock`.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

@app.command()
def sync(
    config_file: Annotated[
        str,
        typer.Option(
            "--config",
            "-c",
            help="Path to the LiteLLM YAML configuration file.",
        ),
    ] = "litellm_config.yaml",
):
    """Sync a local LiteLLM config file to Bitwarden.
    
    Reads the specified YAML file and creates or updates corresponding
    secure notes in the configured Bitwarden folder.
    """
    if not os.path.exists(config_file):
        typer.secho(f"Config file not found: {config_file}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    
    typer.secho(f"Starting sync from '{config_file}' to Bitwarden...", fg=typer.colors.CYAN)
    sync_to_bitwarden(config_file)

@app.command()
def pull(
    output_format: Annotated[
        str,
        typer.Option(
            "--format",
            "-f",
            help="The output format for the pulled data.",
        ),
    ] = "litellm",
    output_file: Annotated[
        str,
        typer.Option(
            "--out",
            "-o",
            help="Path to save the output file. If not provided, prints to console.",
        ),
    ] = None,
):
    """Pull model configurations from Bitwarden.

    Fetches all model configs from the configured Bitwarden folder
    and formats them as specified.
    """
    allowed_formats = ["litellm", "claude-router", "json"]
    if output_format not in allowed_formats:
        typer.secho(f"Invalid format. Allowed formats are: {allowed_formats}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.secho(f"Pulling data from Bitwarden to format as '{output_format}'...", fg=typer.colors.CYAN)
    pull_from_bitwarden(output_format, output_file)

if __name__ == "__main__":
    app()
