import os

TORA_BASE_URL: str = os.getenv("TORA_BASE_URL", "https://tora-api-1030250455947.us-central1.run.app/api")
TORA_API_KEY: str | None = os.getenv("TORA_API_KEY", None)
