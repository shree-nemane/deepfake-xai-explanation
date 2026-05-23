# Migration 001_schema_init
import logging

logger = logging.getLogger(__name__)

def upgrade():
    logger.info("Upgrading core Report, AgentOutput, and EvidenceSegment schemas.")
