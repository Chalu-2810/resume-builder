"""Configuration management for AI Resume Tailor."""
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional

load_dotenv()


class AppConfig(BaseModel):
    """Application configuration."""
    
    google_api_key: str = Field(default="", description="Google Gemini API key")
    libreoffice_path: Optional[str] = Field(default=None, description="Path to LibreOffice executable")
    temp_dir: str = Field(default="./temp", description="Directory for temporary files")
    gemini_model: str = Field(default="gemini-1.5-flash", description="Gemini model to use")
    
    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create configuration from environment variables."""
        return cls(
            google_api_key=os.getenv("GOOGLE_API_KEY", ""),
            libreoffice_path=os.getenv("LIBREOFFICE_PATH"),
            temp_dir=os.getenv("TEMP_DIR", "./temp"),
        )
    
    def validate(self) -> bool:
        """Validate configuration."""
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY is required")
        os.makedirs(self.temp_dir, exist_ok=True)
        return True


# Global configuration instance
config = AppConfig.from_env()