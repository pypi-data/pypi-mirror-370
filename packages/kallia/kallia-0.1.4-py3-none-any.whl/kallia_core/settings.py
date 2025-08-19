import os
import dotenv

dotenv.load_dotenv(dotenv.find_dotenv(usecwd=True))

KALLIA_PROVIDER_API_KEY = os.getenv("KALLIA_PROVIDER_API_KEY", "ollama")
KALLIA_PROVIDER_BASE_URL = os.getenv(
    "KALLIA_PROVIDER_BASE_URL", "http://localhost:11434/v1"
)
KALLIA_PROVIDER_MODEL = os.getenv("KALLIA_PROVIDER_MODEL", "qwen2.5vl:32b")
