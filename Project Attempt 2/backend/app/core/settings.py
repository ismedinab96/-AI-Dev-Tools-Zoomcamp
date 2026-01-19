from pydantic import BaseModel
import os

class Settings(BaseModel):
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./dev.db")
    jwt_secret: str = os.getenv("JWT_SECRET", "dev-secret-change-me")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_exp_minutes: int = int(os.getenv("JWT_EXP_MINUTES", "240"))
    cors_allow_origins: list[str] = [
        os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
    ][0]

settings = Settings()
