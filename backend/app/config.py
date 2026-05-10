import json
from typing import List, Union, Any
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "AfyaDirect"
    APP_ENV: str = "development"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS & Security - Using Union[List[str], str] is CRITICAL to avoid early JSONDecodeErrors
    ALLOWED_ORIGINS: Union[List[str], str] = ["http://localhost:3000"]
    ALLOWED_HOSTS: Union[List[str], str] = ["localhost"]
    ALLOWED_FILE_TYPES: Union[List[str], str] = ["image/jpeg", "image/png", "application/pdf"]
    
    # Firebase
    FIREBASE_CREDENTIALS_PATH: str = "firebase-adminsdk.json"
    FIREBASE_STORAGE_BUCKET: str = "afyadirect.appspot.com"
    FIRESTORE_DB: str = "afyadirect"
    # ADD THIS LINE:
    FIREBASE_WEB_API_KEY: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024
    
    # Payment / SMS (Placeholders)
    MPESA_CONSUMER_KEY: str = ""
    MPESA_CONSUMER_SECRET: str = ""

    @field_validator("ALLOWED_ORIGINS", "ALLOWED_HOSTS", "ALLOWED_FILE_TYPES", mode="before")
    @classmethod
    def parse_env_list(cls, v: Any) -> List[str]:
        # 1. If it's already a list (from default values), return it
        if isinstance(v, list):
            return v
        
        if isinstance(v, str):
            v = v.strip()
            
            # 2. Remove outer single/double quotes often added by Docker/Shell
            if (v.startswith("'") and v.endswith("'")) or (v.startswith('"') and v.endswith('"')):
                v = v[1:-1].strip()

            # 3. Handle JSON-like list strings
            if v.startswith("["):
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    # Fallback: strip brackets and treat as a normal comma-separated string
                    v = v.strip("[]")
            
            # 4. Handle comma-separated values (even if they have internal quotes)
            return [x.strip().strip("'").strip('"') for x in v.split(",") if x.strip()]
        
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()