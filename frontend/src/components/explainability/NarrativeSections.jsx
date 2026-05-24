import React, { useMemo } from 'react';

const SECTION_ORDER = [
  'Finding',
  'Evidence',
  'Reliability',
  'Confidence',
  'Contradictions',
  'Explainability',
];

const parseStructuredSummary = (structuredSummary) => {
  if (!structuredSummary || typeof structuredSummary !== 'string') return [];

  const sections = [];
  const parts = structuredSummary.split(/^## /m).filter(Boolean);

  parts.forEach((part) => {
    const newline = part.indexOf('\n');
    const title = newline === -1 ? part.trim() : part.slice(0, newline).trim();
    const body = newline === -1 ? '' : part.slice(newline + 1).trim();
    if (title) sections.push({ title, body });
  });

  return sections;
};

const NarrativeSections = ({ result }) => {
  const narrative = result?.narrative;
  const sections = useMemo(
    () => parseStructuredSummary(narrative?.structured_summary),
    [narrative?.structured_summary],
  );

  const orderedSections = useMemo(() => {
    if (!sections.length) return [];
    const byTitle = Object.fromEntries(sections.map((s) => [s.title, s]));
    const ordered = SECTION_ORDER.filter((name) => byTitle[name]).map((name) => byTitle[name]);
    const extras = sections.filter((s) => !SECTION_ORDER.includes(s.title));
    return [...ordered, ...extras];
  }, [sections]);

  if (!narrative) {
    return (
      <section className="explanation-section">
        <h3 className="panel-title">Forensic Narrative</h3>
        <p className="drawer-empty">No narrative available for this report.</p>
      </section>
    );
  }

  if (!orderedSections.length) {
    return (
      <section className="explanation-section">
        <h3 className="panel-title">Forensic Narrative</h3>
        <div className="narrative-section glass">
          <p className="narrative-body">{narrative.human_summary || 'No narrative text available.'}</p>
        </div>
      </section>
    );
  }

  return (
    <section className="explanation-section">
      <h3 className="panel-title">Forensic Narrative</h3>
      <div className="narrative-grid">
        {orderedSections.map((section) => (
          <article key={section.title} className="narrative-section glass">
            <h4>{section.title}</h4>
            <p className="narrative-body">{section.body}</p>
          </article>
        ))}
      </div>
    </section>
  );
};

export default NarrativeSections;
