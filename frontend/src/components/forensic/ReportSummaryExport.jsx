import React, { useState } from 'react';
import { Copy, Check } from 'lucide-react';
import { buildExportableReportSummary } from '../../utils/chunkEvidence';

const ReportSummaryExport = ({ result }) => {
  const [copied, setCopied] = useState(false);
  const summaryText = buildExportableReportSummary(result);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(summaryText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Copy failed', err);
    }
  };

  const handleDownload = () => {
    const blob = new Blob([summaryText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `forensic-report-${result?.id || 'export'}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <section className="report-export-panel glass">
      <div className="report-export-header">
        <h3>Report summary</h3>
        <div className="report-export-actions">
          <button type="button" className="btn btn-secondary btn-sm" onClick={handleCopy}>
            {copied ? <Check size={14} /> : <Copy size={14} />}
            {copied ? 'Copied' : 'Copy'}
          </button>
          <button type="button" className="btn btn-secondary btn-sm" onClick={handleDownload}>
            Download .txt
          </button>
        </div>
      </div>
      <pre className="report-export-preview">{summaryText || 'No report data to export.'}</pre>
    </section>
  );
};

export default ReportSummaryExport;
