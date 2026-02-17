export function formatCurrency(value) {
  if (value == null) return '—';
  const abs = Math.abs(value);
  if (abs >= 1_000_000_000) return `S$${(value / 1_000_000_000).toFixed(1)}B`;
  if (abs >= 1_000_000) return `S$${(value / 1_000_000).toFixed(1)}M`;
  if (abs >= 1_000) return `S$${(value / 1_000).toFixed(0)}K`;
  return `S$${value.toLocaleString()}`;
}

export function formatNumber(value) {
  if (value == null) return '—';
  return value.toLocaleString();
}

export function formatPercent(value) {
  if (value == null) return '—';
  return `${value.toFixed(1)}%`;
}

export function formatCompactCurrency(value) {
  if (value == null) return '—';
  const abs = Math.abs(value);
  if (abs >= 1_000_000_000) return `$${(value / 1_000_000_000).toFixed(1)}B`;
  if (abs >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`;
  if (abs >= 1_000) return `$${(value / 1_000).toFixed(0)}K`;
  return `$${value.toLocaleString()}`;
}
