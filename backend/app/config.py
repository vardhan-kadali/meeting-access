import os
import json
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Any

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.8-flash"
    # Using Any prevents pydantic-settings from eagerly running json.loads on complex types
    # prior to our custom field_validator, enabling transparent comma-separated and JSON list support.
    GEMINI_FALLBACK_MODELS: Any = ["gemini-3.5-flash-lite"]
    CORS_ORIGINS: Any = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Model Retry & Fallback Settings
    MAX_RETRIES_PER_MODEL: int = 2
    RETRY_INITIAL_DELAY: float = 1.0

    # PDF Processing Limits
    MAX_UPLOAD_SIZE_MB: int = 15
    MAX_PAGE_COUNT: int = 100

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> List[str]:
        raw_items: List[str] = []
        if isinstance(v, str):
            v_clean = v.strip()
            if not v_clean or v_clean.lower() in ("none", "null", "false", "[]"):
                return []
            if v_clean == "*":
                return ["*"]
            if v_clean.startswith("[") or v_clean.startswith("{"):
                try:
                    parsed = json.loads(v_clean)
                except Exception as e:
                    raise ValueError(f"Invalid JSON in CORS_ORIGINS: {e}") from e
                if not isinstance(parsed, list):
                    raise ValueError("JSON in CORS_ORIGINS must be a list of origins")
                raw_items = [str(orig).strip() for orig in parsed]
            else:
                raw_items = [orig.strip() for orig in v_clean.split(",")]
        elif isinstance(v, list):
            raw_items = [str(orig).strip() for orig in v]
        elif v is None:
            return []

        deduped: List[str] = []
        for item in raw_items:
            if item and item not in deduped:
                deduped.append(item)
        return deduped

    @field_validator("GEMINI_FALLBACK_MODELS", mode="before")
    @classmethod
    def parse_fallback_models(cls, v: Any) -> List[str]:
        raw_items: List[str] = []
        if isinstance(v, str):
            v_clean = v.strip()
            if not v_clean or v_clean.lower() in ("none", "null", "false", "[]"):
                return []
            if v_clean.startswith("[") or v_clean.startswith("{"):
                try:
                    parsed = json.loads(v_clean)
                except Exception as e:
                    raise ValueError(f"Invalid JSON in GEMINI_FALLBACK_MODELS: {e}") from e
                if not isinstance(parsed, list):
                    raise ValueError("JSON in GEMINI_FALLBACK_MODELS must be a list of model names")
                raw_items = [str(m).strip() for m in parsed]
            else:
                raw_items = [m.strip() for m in v_clean.split(",")]
        elif isinstance(v, list):
            raw_items = [str(m).strip() for m in v]
        elif v is None:
            return []
        else:
            raise ValueError(f"Unsupported type for GEMINI_FALLBACK_MODELS: {type(v)}")

        deduped: List[str] = []
        for item in raw_items:
            if item and item.lower() not in ("none", "null") and item not in deduped:
                deduped.append(item)
        return deduped

    @property
    def model_chain(self) -> List[str]:
        """
        Returns the ordered list of unique models to attempt:
        Primary model first, followed by configured fallback models.
        """
        chain: List[str] = []
        if self.GEMINI_MODEL and self.GEMINI_MODEL.strip():
            chain.append(self.GEMINI_MODEL.strip())
        for fallback in self.GEMINI_FALLBACK_MODELS:
            if isinstance(fallback, str) and fallback.strip():
                clean_m = fallback.strip()
                if clean_m not in chain and clean_m.lower() not in ("none", "null"):
                    chain.append(clean_m)
        return chain or ["gemini-3.8-flash"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
