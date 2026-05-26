import { normalizeDiagnostics } from './diagnostics';

const melKey = (chunk) => `${chunk.start_time}:${chunk.end_time}`;

/** Prepare API report payloads for safe React rendering. */
export const normalizeReport = (raw) => {
  if (!raw || typeof raw !== 'object') return raw;

  const melMap = raw.mel_previews || {};
  const timeline = (raw.timeline || []).map((chunk) => {
    const key = melKey(chunk);
    const mel = chunk.mel_preview_base64 || melMap[key] || null;
    const { mel_preview_base64, ...rest } = chunk;
    return mel ? { ...rest, mel_preview_base64: mel } : rest;
  });

  const { mel_previews, ...rest } = raw;

  return {
    ...rest,
    timeline,
    diagnostics: normalizeDiagnostics(raw.diagnostics),
  };
};

/** Re-attach mel previews from the raw API payload (live job result only). */
export const mergeMelPreviews = (normalized, raw) => {
  if (!normalized || !raw?.timeline?.length) return normalized;
  const timeline = normalized.timeline.map((chunk, i) => ({
    ...chunk,
    mel_preview_base64: raw.timeline[i]?.mel_preview_base64 || null,
  }));
  return { ...normalized, timeline };
};
