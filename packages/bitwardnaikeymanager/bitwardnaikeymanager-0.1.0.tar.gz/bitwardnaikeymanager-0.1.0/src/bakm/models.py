from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# --- LiteLLM Models ---

class LiteLLMParams(BaseModel):
    model: str
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    api_version: Optional[str] = None
    # Allow any other parameters
    class Config:
        extra = 'allow'

class LiteLLMModel(BaseModel):
    model_name: str
    litellm_params: LiteLLMParams

class LiteLLMConfig(BaseModel):
    model_list: List[LiteLLMModel]
    # Using dict for litellm_settings to be flexible
    litellm_settings: Optional[Dict[str, Any]] = None


# --- Claude Code Router Model ---

class ClaudeRouterModel(BaseModel):
    name: str
    provider: str
    api_key: str
    api_base: Optional[str] = None
    api_version: Optional[str] = None
    # Allow other fields as they might be added
    class Config:
        extra = 'allow'

class ClaudeRouterConfig(BaseModel):
    models: List[ClaudeRouterModel]


# --- Generic Model for Bitwarden representation ---

class BitwardenModel(BaseModel):
    name: str
    # Fields will contain api_key, api_base, etc.
    fields: Dict[str, Any]
