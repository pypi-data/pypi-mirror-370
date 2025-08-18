import yaml
import json
from typing import Dict, Any, List

from .bitwarden import BitwardenCLI
from .models import LiteLLMConfig, BitwardenModel
from .config import BITWARDEN_FOLDER_NAME

def _to_bitwarden_item(model_config: Dict[str, Any], folder_id: str) -> Dict[str, Any]:
    """Converts a model's config to a Bitwarden item structure."""
    fields = []
    # Securely store the API key as a hidden custom field
    if model_config.get("api_key"):
        fields.append({"name": "api_key", "value": model_config["api_key"], "type": 1}) # type 1 is hidden
    
    # Store other params as text fields
    for key, value in model_config.items():
        if key not in ["api_key"] and value is not None:
            fields.append({"name": key, "value": str(value), "type": 0}) # type 0 is text

    return {
        "folderId": folder_id,
        "type": 2,  # Secure Note
        "name": model_config["model_name"],
        "notes": "LiteLLM model configuration.",
        "fields": fields,
        "secureNote": {
            "type": 0
        },
    }

def sync_to_bitwarden(config_path: str):
    """Syncs a LiteLLM YAML config file to Bitwarden."""
    bw = BitwardenCLI()
    if not bw.is_logged_in():
        print("Please log in to the Bitwarden CLI first.")
        return

    try:
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        llm_config = LiteLLMConfig(**config_data)
    except Exception as e:
        print(f"Error reading or parsing config file {config_path}: {e}")
        return

    folder_id = bw.get_folder_id(BITWARDEN_FOLDER_NAME)
    if not folder_id:
        print(f"Folder '{BITWARDEN_FOLDER_NAME}' not found. Attempting to create it...")
        created_folder = bw.create_folder(BITWARDEN_FOLDER_NAME)
        if created_folder and created_folder.get("id"):
            folder_id = created_folder.get("id")
            print(f"Folder '{BITWARDEN_FOLDER_NAME}' created successfully with ID: {folder_id}")
            # A sync after creation is good practice
            bw.sync()
        else:
            print(f"Failed to create folder '{BITWARDEN_FOLDER_NAME}'. Please check your permissions and try again.")
            return

    print(f"Found folder '{BITWARDEN_FOLDER_NAME}' with ID: {folder_id}")
    existing_items = {item['name']: item for item in bw.get_items_in_folder(folder_id)}

    for model in llm_config.model_list:
        model_name = model.model_name
        params = model.litellm_params.dict()
        params['model_name'] = model_name # Add model_name to the params for storage

        item_data = _to_bitwarden_item(params, folder_id)

        if model_name in existing_items:
            print(f"Updating item: {model_name}")
            item_id = existing_items[model_name]['id']
            bw.update_item(item_id, item_data)
        else:
            print(f"Creating new item: {model_name}")
            bw.create_item(item_data)

    print("\nSync to Bitwarden complete.")


# --- Pull Logic ---

def _from_bitwarden_item(item: Dict[str, Any]) -> BitwardenModel:
    """Converts a Bitwarden item back to our internal model representation."""
    fields = {}
    if item.get("fields"):
        for field in item["fields"]:
            fields[field["name"]] = field["value"]
    return BitwardenModel(name=item["name"], fields=fields)

def _to_litellm_yaml(models: List[BitwardenModel]) -> str:
    """Converts a list of models to a LiteLLM YAML string."""
    model_list = []
    for model in models:
        params = model.fields
        model_name = model.name
        # model_name is a field, remove it from litellm_params
        if 'model_name' in params:
            del params['model_name']

        model_list.append({
            "model_name": model_name,
            "litellm_params": params
        })
    
    config = {"model_list": model_list}
    return yaml.dump(config, sort_keys=False)

def _to_claude_router_json(models: List[BitwardenModel]) -> str:
    """Converts a list of models to a Claude Code Router JSON string."""
    router_models = []
    for model in models:
        # Heuristic to determine provider from model name
        provider = "unknown"
        if "azure" in model.name.lower():
            provider = "azure"
        elif "openai" in model.name.lower():
            provider = "openai"
        elif "anthropic" in model.name.lower():
            provider = "anthropic"
        
        router_models.append({
            "name": model.name,
            "provider": provider,
            **model.fields
        })
    
    config = {"models": router_models}
    return json.dumps(config, indent=2)

def _to_generic_json(models: List[BitwardenModel]) -> str:
    """Converts a list of models to a generic JSON string."""
    return json.dumps([model.dict() for model in models], indent=2)


def pull_from_bitwarden(output_format: str, output_file: str = None):
    """Pulls configurations from Bitwarden and formats them."""
    bw = BitwardenCLI()
    if not bw.is_logged_in():
        print("Please log in to the Bitwarden CLI first.")
        return

    folder_id = bw.get_folder_id(BITWARDEN_FOLDER_NAME)
    if not folder_id:
        print(f"Folder '{BITWARDEN_FOLDER_NAME}' not found.")
        return

    items = bw.get_items_in_folder(folder_id)
    if not items:
        print(f"No items found in folder '{BITWARDEN_FOLDER_NAME}'.")
        return

    models = [_from_bitwarden_item(item) for item in items]

    output_content = ""
    if output_format == "litellm":
        output_content = _to_litellm_yaml(models)
    elif output_format == "claude-router":
        output_content = _to_claude_router_json(models)
    elif output_format == "json":
        output_content = _to_generic_json(models)
    else:
        print(f"Unknown output format: {output_format}")
        return

    if output_file:
        try:
            with open(output_file, 'w') as f:
                f.write(output_content)
            print(f"Output successfully written to {output_file}")
        except Exception as e:
            print(f"Error writing to file {output_file}: {e}")
    else:
        print(output_content)
