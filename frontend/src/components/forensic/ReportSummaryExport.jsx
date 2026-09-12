import React, { useState } from 'react';
import { Copy, Check, Download, FileJson, ShieldCheck } from 'lucide-react';
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

  const handleDownloadTxt = () => {
    const blob = new Blob([summaryText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `forensic-audit-${result?.id || 'case'}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleDownloadJson = () => {
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `forensic-evidence-${result?.id || 'case'}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="glass p-5 rounded-xl flex items-center justify-between gap-4 flex-wrap">
      <div className="flex items-center gap-3 min-w-0">
        <div className="w-10 h-10 rounded-lg bg-primary/15 flex items-center justify-center shrink-0 text-primary">
          <ShieldCheck size={20} />
        </div>
        <div>
          <h4 className="text-sm font-bold text-white mb-0.5">Forensic Case Dossier &amp; Export</h4>
          <p className="text-xs text-muted font-mono">
            Case ID: <span className="text-white font-bold">{result?.id ? `#${String(result.id).slice(-8)}` : 'N/A'}</span>
            {result?.filename && ` · File: ${result.filename}`}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2 flex-wrap">
        <button 
          type="button" 
          className="btn btn-ghost btn-sm" 
          onClick={handleCopy}
          title="Copy executive summary text to clipboard"
        >
          {copied ? <Check size={14} className="text-success" /> : <Copy size={14} />}
          <span>{copied ? 'Copied' : 'Copy Summary'}</span>
        </button>

        <button 
          type="button" 
          className="btn btn-ghost btn-sm" 
          onClick={handleDownloadTxt}
          title="Download complete text report"
        >
          <Download size={14} />
          <span>Audit Report (.txt)</span>
        </button>

        <button 
          type="button" 
          className="btn btn-primary btn-sm" 
          onClick={handleDownloadJson}
          title="Download raw forensic telemetry and feature vectors as JSON"
        >
          <FileJson size={14} />
          <span>Evidence JSON</span>
        </button>
      </div>
    </div>
  );
};

export default ReportSummaryExport;
