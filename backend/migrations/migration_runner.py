import logging
import importlib
from backend.persistence.database import init_db

logger = logging.getLogger(__name__)

def run_migrations():
    logger.info("Initializing database base schema...")
    init_db() # Initializes SQLAlchemy metadata creations
    logger.info("Database base schema initialized successfully.")

    versions = ["001_schema_init", "002_xai_schema", "003_consensus_schema"]
    logger.info(f"Running migrations: {versions}")
    for ver in versions:
        try:
            module = importlib.import_module(f"backend.migrations.versions.{ver}")
            if hasattr(module, "upgrade"):
                logger.info(f"Applying migration: {ver}")
                module.upgrade()
                logger.info(f"Migration {ver} applied successfully.")
        except Exception as e:
            logger.error(f"Error applying migration {ver}: {e}")
            raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_migrations()
