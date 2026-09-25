from sqlalchemy import text

from src.config.database import engine
from src.utils.logger import get_logger

logger = get_logger(__name__)

NEW_COLUMNS = {
    "ai_recommendation": "VARCHAR(20) NULL",
    "ai_rationale": "TEXT NULL",
}


def _column_exists(conn, table, column):
    result = conn.execute(
        text(
            "SELECT COUNT(*) FROM information_schema.columns "
            "WHERE table_schema = DATABASE() AND table_name = :table AND column_name = :column"
        ),
        {"table": table, "column": column},
    )
    exists = result.scalar() > 0
    return exists


def run():
    with engine.begin() as conn:
        for column_name, column_def in NEW_COLUMNS.items():
            if _column_exists(conn, "claims_history", column_name):
                logger.info(f"Column claims_history.{column_name} already exists, skipping")
                continue
            conn.execute(text(f"ALTER TABLE claims_history ADD COLUMN {column_name} {column_def}"))
            logger.info(f"Added column claims_history.{column_name}")

    logger.info("Migration complete.")


if __name__ == "__main__":
    run()


