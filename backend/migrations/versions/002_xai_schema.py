# Migration 002_xai_schema
import logging

logger = logging.getLogger(__name__)

def upgrade():
    logger.info("Upgrading XAIArtifact and NarrativeReport schemas (decoupled from reports).")
