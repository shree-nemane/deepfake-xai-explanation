#!/usr/bin/env python3
"""Extract a redacted analysis report from forensic_intelligence.db for documentation."""

import argparse
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "forensic_intelligence.db"
REDACT_KEYS = {"heatmap_base64", "mel_preview_base64"}
REDACT_TOP = {"mel_previews"}


def redact(obj, parent_key=None):
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k in REDACT_TOP:
                out[k] = {kk: f"<base64 png, {len(vv)} chars>" for kk, vv in (v or {}).items()}
            elif k in REDACT_KEYS and isinstance(v, str):
                out[k] = f"<base64, {len(v)} chars>"
            else:
                out[k] = redact(v, k)
        return out
    if isinstance(obj, list):
        return [redact(i, parent_key) for i in obj]
    return obj


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report-id", help="Report UUID (default: latest)")
    parser.add_argument("--out", default="docs/sample_report_redacted.json")
    args = parser.parse_args()

    if not DB.exists():
        raise SystemExit(f"Database not found: {DB}")

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    if args.report_id:
        row = conn.execute(
            "SELECT id, filename, created_at, full_response FROM reports WHERE id=?",
            (args.report_id,),
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT id, filename, created_at, full_response FROM reports ORDER BY created_at DESC LIMIT 1"
        ).fetchone()
    conn.close()

    if not row or not row["full_response"]:
        raise SystemExit("Report not found or empty full_response")

    payload = json.loads(row["full_response"])
    sample = {
        "report_id": row["id"],
        "filename": row["filename"],
        "created_at": row["created_at"],
        "payload": redact(payload),
    }

    out_path = ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(sample, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"  report_id={row['id']} filename={row['filename']}")
    print(f"  verdict={payload.get('consensus', {}).get('verdict')}")


if __name__ == "__main__":
    main()
