from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


class Settings:
    APP_NAME = os.getenv("APP_NAME", "MediExtract AI")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    DEBUG = os.getenv("DEBUG", "true")
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    MONGODB_URL = os.getenv("MONGODB_URL")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "mediextract")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    )


settings = Settings()