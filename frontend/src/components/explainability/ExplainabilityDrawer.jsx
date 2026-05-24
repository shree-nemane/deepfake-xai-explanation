import React from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { X } from 'lucide-react';
import ShapContributionPanel from './ShapContributionPanel';
import CounterfactualPanel from './CounterfactualPanel';
import PlotlyEvidenceGraph from './PlotlyEvidenceGraph';

const ExplainabilityDrawer = ({ open, onClose, result }) => {
  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.button
            type="button"
            className="drawer-backdrop"
            aria-label="Close explainability drawer"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />
          <motion.aside
            className="explainability-drawer glass"
            role="dialog"
            aria-modal="true"
            aria-label="Explainability Console"
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'tween', duration: 0.2 }}
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
              <PlotlyEvidenceGraph evidenceGraph={result?.xai?.evidence_graph} />
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
};

export default ExplainabilityDrawer;
