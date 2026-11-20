import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Union

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.8-flash"
    GEMINI_FALLBACK_MODELS: List[str] = ["gemini-3.5-flash-lite"]
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Model Retry & Fallback Settings
    MAX_RETRIES_PER_MODEL: int = 2
    RETRY_INITIAL_DELAY: float = 1.0

    # PDF Processing Limits
    MAX_UPLOAD_SIZE_MB: int = 15
    MAX_PAGE_COUNT: int = 100

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [orig.strip() for orig in v.split(",") if orig.strip()]
        return v

    @field_validator("GEMINI_FALLBACK_MODELS", mode="before")
    @classmethod
    def parse_fallback_models(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            v = v.strip()
            if not v or v.lower() in ("none", "null", "false", "[]"):
                return []
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [m.strip() for m in v.split(",") if m.strip()]
        return v

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
