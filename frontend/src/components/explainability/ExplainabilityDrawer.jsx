import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { X } from 'lucide-react';
import ShapContributionPanel from './ShapContributionPanel';
import CounterfactualPanel from './CounterfactualPanel';
import PlotlyEvidenceGraph from './PlotlyEvidenceGraph';
import DrawerErrorBoundary from './DrawerErrorBoundary';

const ExplainabilityDrawer = ({ open, onClose, result }) => {
  const [showPlotly, setShowPlotly] = useState(false);

  useEffect(() => {
    if (!open) {
      setShowPlotly(false);
      document.body.classList.remove('drawer-open');
      return undefined;
    }
    document.body.classList.add('drawer-open');
    const timer = window.setTimeout(() => setShowPlotly(true), 280);
    return () => {
      window.clearTimeout(timer);
      document.body.classList.remove('drawer-open');
    };
  }, [open]);

  useEffect(() => {
    if (!open) return undefined;
    const onKey = (e) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open, onClose]);

  const content = (
    <AnimatePresence>
      {open && (
        <div className="drawer-root" role="presentation">
          <motion.div
            className="drawer-backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            aria-hidden
          />
          <motion.aside
            className="explainability-drawer glass"
            role="dialog"
            aria-modal="true"
            aria-label="Explainability Console"
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'tween', duration: 0.22 }}
            onClick={(e) => e.stopPropagation()}
          >
            <header className="drawer-header">
              <div>
                <h3>Explainability Console</h3>
                <p className="drawer-caption">SHAP, sensitivity, and evidence graph</p>
              </div>
              <button type="button" className="drawer-close-btn" onClick={onClose} aria-label="Close">
                <X size={20} />
              </button>
            </header>

            <div className="drawer-body">
              <ShapContributionPanel result={result} />
              <CounterfactualPanel result={result} />
              <DrawerErrorBoundary
                evidenceGraph={result?.xai?.evidence_graph}
                agents={result?.agents}
                consensus={result?.consensus}
                diagnostics={result?.diagnostics}
              >
                {showPlotly ? (
                  <PlotlyEvidenceGraph evidenceGraph={result?.xai?.evidence_graph} />
                ) : (
                  <section className="drawer-section">
                    <p className="drawer-caption">Loading interactive graph…</p>
                  </section>
                )}
              </DrawerErrorBoundary>
            </div>
          </motion.aside>
        </div>
      )}
    </AnimatePresence>
  );

  if (typeof document === 'undefined') return null;
  return createPortal(content, document.body);
};

export default ExplainabilityDrawer;
