import os
from dataclasses import dataclass
from dotenv import load_dotenv
from logger import logger  

# Load environment variables
load_dotenv()

@dataclass
class Config:
    """Application configuration using dataclass"""
    HOST: str 
    PORT: int
    UPLOAD_DIR: str
    API_URL: str
    GROQ_API_KEY: int 
    GROQ_API_URL: str 
    MODEL: str 
        

    @classmethod
    def from_env(cls) -> 'Config':
        """Create config from environment variables"""
        config = cls(
            HOST=os.getenv("HOST"),
            PORT=int(os.getenv("PORT")),
            UPLOAD_DIR=os.getenv("UPLOAD_DIR", "uploads"), 
            API_URL=os.getenv("API_URL"),
            GROQ_API_KEY=os.getenv("GROQ_API_KEY"),
            GROQ_API_URL=os.getenv("GROQ_API_URL"), 
            MODEL=os.getenv("MODEL")
            )
        
        logger.info("Configuration loaded from environment variables")

        if not config.api_key :
            logger.error("Missing critical config values: API_KEY ")
            raise ValueError("Missing critical environment variables: API_KEY ")

        return config

config = Config.from_env()