# Migration 003_consensus_schema
import logging

logger = logging.getLogger(__name__)

def upgrade():
    logger.info("Upgrading ConsensusEvent and EventAgentDetails schemas for contradiction warning details.")
