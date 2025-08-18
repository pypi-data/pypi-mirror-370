import subprocess
import json
import sys
import base64
from typing import Any, Dict, List, Optional

class BitwardenCLI:
    """A wrapper for the Bitwarden CLI (`bw`)."""

    def __init__(self):
        self._check_cli_installed()

    def _check_cli_installed(self):
        """Check if the `bw` CLI is installed and available in the PATH."""
        try:
            subprocess.run(
                ["bw", "--version"],
                check=True,
                capture_output=True,
                text=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(
                "Error: Bitwarden CLI (`bw`) is not installed or not in your PATH.",
                file=sys.stderr,
            )
            print("Please install it from: https://bitwarden.com/help/cli/", file=sys.stderr)
            sys.exit(1)

    def _run_command(self, command: List[str], suppress_error: bool = False) -> Optional[Dict[str, Any]]:
        """Run a `bw` command and return its JSON output."""
        try:
            # Always add --raw to get clean JSON output
            process = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )
            # The --raw flag in bw sometimes returns empty string instead of valid json
            if not process.stdout.strip():
                return None
            return json.loads(process.stdout)
        except subprocess.CalledProcessError as e:
            if not suppress_error:
                print(f"Error executing command: {' '.join(command)}", file=sys.stderr)
                print(f"Stderr: {e.stderr}", file=sys.stderr)
            return None
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from command: {' '.join(command)}", file=sys.stderr)
            return None

    def is_logged_in(self) -> bool:
        """Check if the user is logged into the CLI."""
        # Use `bw status` which is a reliable way to check lock status
        status = self._run_command(["bw", "status"], suppress_error=True)
        # The user is logged in if the status is "unlocked" or "locked"
        return status is not None and status.get("status") in ["unlocked", "locked"]

    def sync(self) -> bool:
        """Sync the vault with the Bitwarden server."""
        print("Syncing vault...")
        result = self._run_command(["bw", "sync"], suppress_error=True)
        if result is None:
            print("Sync failed. Please check your connection and credentials.", file=sys.stderr)
            return False
        print("Sync complete.")
        return True

    def get_folder_id(self, folder_name: str) -> Optional[str]:
        """Get the ID of a folder by its name."""
        folders = self._run_command(["bw", "list", "folders"])
        if folders:
            for folder in folders:
                if folder.get("name") == folder_name:
                    return folder.get("id")
        return None

    def get_items_in_folder(self, folder_id: str) -> List[Dict[str, Any]]:
        """Get all items (secure notes) within a specific folder."""
        items = self._run_command(["bw", "list", "items", "--folderid", folder_id])
        return items if items else []

    def create_folder(self, folder_name: str) -> Optional[Dict[str, Any]]:
        """Create a new folder in the vault."""
        print(f"Creating folder '{folder_name}' in Bitwarden...")
        folder_data = {"name": folder_name}
        folder_json = json.dumps(folder_data)
        encoded_folder_json = base64.b64encode(folder_json.encode("utf-8")).decode("utf-8")
        return self._run_command(["bw", "create", "folder", encoded_folder_json])

    def create_item(self, item_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new item (secure note) in the vault."""
        item_json = json.dumps(item_data)
        encoded_item_json = base64.b64encode(item_json.encode("utf-8")).decode("utf-8")
        return self._run_command(["bw", "create", "item", encoded_item_json])

    def update_item(self, item_id: str, item_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing item (secure note)."""
        item_json = json.dumps(item_data)
        encoded_item_json = base64.b64encode(item_json.encode("utf-8")).decode("utf-8")
        return self._run_command(["bw", "edit", "item", item_id, encoded_item_json])
