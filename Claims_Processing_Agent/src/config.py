import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
POLICIES_DIR = DATA_DIR / "policies"
CLAIMS_HISTORY_CSV = DATA_DIR / "claims_history.csv"

LOGS_DIR = BASE_DIR / "logs"
AUDIT_LOG_FILE = LOGS_DIR / "audit_log.csv"

# Where ChromaDB will save the vector store to disk, so we don't have to  re-embed all the policy documents every time we run the app.
CHROMA_PERSIST_DIR = BASE_DIR / "chroma_store"
CHROMA_COLLECTION_NAME = "motor_insurance_policies"

# API keys / model settings
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL_NAME = "openai/gpt-oss-120b"

# Business rules
# If a customer has filed this many similar claims within the given window, our fraud tool will flag it for review.
FRAUD_REPEAT_CLAIM_THRESHOLD = 3
FRAUD_REPEAT_CLAIM_WINDOW_DAYS = 180

# If a claim is filed this soon after a policy starts, we flag it for review as a possible pre-existing-damage case.
EARLY_CLAIM_WINDOW_DAYS = 7


def ensure_folders_exist():
    """Creates the logs and chroma_store folders if they don't exist yet."""
    LOGS_DIR.mkdir(exist_ok=True)
    CHROMA_PERSIST_DIR.mkdir(exist_ok=True)