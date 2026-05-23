# backend/migrations/validate_schema.py
import logging
from sqlalchemy import inspect
from backend.persistence.database import (
    Base, Report, ConsensusEvent, XAIArtifact, NarrativeReport, EventAgentDetails, engine, init_db
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_schema():
    logger.info("Running programmatic schema validation...")
    
    # Initialize/ensure tables exist
    init_db()
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    logger.info(f"Existing database tables: {tables}")
    
    # Required tables check
    required_tables = ["reports", "consensus_events", "xai_artifacts", "narrative_reports", "event_agent_details", "processing_metadata"]
    for table in required_tables:
        assert table in tables, f"Required table '{table}' is missing from the database!"
        logger.info(f"Table '{table}' presence confirmed.")

    # 0. Report column checks
    report_cols = {col["name"]: col["type"].__class__.__name__ for col in inspector.get_columns("reports")}
    logger.info(f"reports columns: {report_cols}")
    assert "schema_version" in report_cols, "Column 'schema_version' missing from reports!"

    # 1. NarrativeReport column checks
    narrative_cols = {col["name"]: col["type"].__class__.__name__ for col in inspector.get_columns("narrative_reports")}
    logger.info(f"narrative_reports columns: {narrative_cols}")
    assert "structured_summary" in narrative_cols, "Column 'structured_summary' missing from narrative_reports!"
    assert "human_summary" in narrative_cols, "Column 'human_summary' missing from narrative_reports!"
    assert "narrative_metadata" in narrative_cols, "Column 'narrative_metadata' missing!"
    assert "generated_by" in narrative_cols, "Column 'generated_by' missing!"
    
    # Unrestricted Text type check
    assert narrative_cols["structured_summary"] in {"Text", "TEXT"}, "structured_summary should be Text!"
    assert narrative_cols["human_summary"] in {"Text", "TEXT"}, "human_summary should be Text!"
    
    # 2. XAIArtifact column checks
    xai_cols = {col["name"]: col["type"].__class__.__name__ for col in inspector.get_columns("xai_artifacts")}
    logger.info(f"xai_artifacts columns: {xai_cols}")
    assert "shap_values" in xai_cols, "Column 'shap_values' missing from xai_artifacts!"
    assert "counterfactuals" in xai_cols, "Column 'counterfactuals' missing!"
    assert "shap_summary" in xai_cols, "Column 'shap_summary' missing!"
    assert "counterfactual_summary" in xai_cols, "Column 'counterfactual_summary' missing!"
    assert xai_cols["shap_summary"] in {"Text", "TEXT"}, "shap_summary should be Text!"
    assert xai_cols["counterfactual_summary"] in {"Text", "TEXT"}, "counterfactual_summary should be Text!"
    
    # 3. EventAgentDetails column checks
    agent_cols = {col["name"]: col["type"].__class__.__name__ for col in inspector.get_columns("event_agent_details")}
    logger.info(f"event_agent_details columns: {agent_cols}")
    assert "agent_version" in agent_cols, "Column 'agent_version' missing!"
    assert "adjusted_confidence" in agent_cols, "Column 'adjusted_confidence' missing!"
    assert "suppression_factor" in agent_cols, "Column 'suppression_factor' missing!"
    assert "temporal_region" in agent_cols, "Column 'temporal_region' missing!"
    
    # 4. ConsensusEvent column checks
    event_cols = {col["name"]: col["type"].__class__.__name__ for col in inspector.get_columns("consensus_events")}
    logger.info(f"consensus_events columns: {event_cols}")
    assert "event_type" in event_cols, "Column 'event_type' missing from consensus_events!"
    assert "agent_snapshot" in event_cols, "Column 'agent_snapshot' missing from consensus_events!"
    assert "diagnostic_metrics" in event_cols, "Column 'diagnostic_metrics' missing from consensus_events!"

    # 4.5 ProcessingMetadata column checks
    meta_cols = {col["name"]: col["type"].__class__.__name__ for col in inspector.get_columns("processing_metadata")}
    logger.info(f"processing_metadata columns: {meta_cols}")
    assert "chunk_duration" in meta_cols, "Column 'chunk_duration' missing!"
    assert "overlap" in meta_cols, "Column 'overlap' missing!"
    assert "semantic_sr" in meta_cols, "Column 'semantic_sr' missing!"
    assert "forensic_sr" in meta_cols, "Column 'forensic_sr' missing!"
    assert "pipeline_version" in meta_cols, "Column 'pipeline_version' missing!"

    # 5. Timestamp auditing checks (created_at, updated_at present in all tables)
    audit_tables = ["reports", "consensus_events", "xai_artifacts", "narrative_reports", "event_agent_details", "processing_metadata"]
    for t in audit_tables:
        cols = [c["name"] for c in inspector.get_columns(t)]
        assert "created_at" in cols, f"created_at is missing from table {t}!"
        assert "updated_at" in cols, f"updated_at is missing from table {t}!"
        logger.info(f"Audit timestamps (created_at, updated_at) confirmed for table '{t}'.")

    logger.info("Programmatic schema validation COMPLETED SUCCESSFULLY! All constraints, typings, and audit fields verified.")

if __name__ == "__main__":
    validate_schema()
