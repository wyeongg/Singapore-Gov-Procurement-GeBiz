import styles from './FilterBar.module.css';

const CATEGORIES = [
  { value: '', label: 'All categories' },
  { value: 'diagnostics', label: 'Diagnostics' },
  { value: 'devices', label: 'Devices' },
  { value: 'consumables', label: 'Consumables' },
  { value: 'pharma_biotech', label: 'Pharma / Biotech' },
  { value: 'dental', label: 'Dental' },
  { value: 'services', label: 'Services' },
  { value: 'general', label: 'General Medical' },
];

export default function FilterBar({ filters, onChange }) {
  const update = (key, value) => {
    onChange({ ...filters, [key]: value || null });
  };

  return (
    <div className={styles.bar}>
      <div className={styles.group}>
        <label className={styles.label}>From</label>
        <input
          type="date"
          className={styles.input}
          value={filters.dateFrom || ''}
          onChange={(e) => update('dateFrom', e.target.value)}
        />
      </div>

      <div className={styles.group}>
        <label className={styles.label}>To</label>
        <input
          type="date"
          className={styles.input}
          value={filters.dateTo || ''}
          onChange={(e) => update('dateTo', e.target.value)}
        />
      </div>

      <div className={styles.group}>
        <label className={styles.label}>Category</label>
        <select
          className={styles.input}
          value={filters.category || ''}
          onChange={(e) => update('category', e.target.value)}
        >
          {CATEGORIES.map((c) => (
            <option key={c.value} value={c.value}>
              {c.label}
            </option>
          ))}
        </select>
      </div>

      <div className={styles.toggle}>
        <label className={styles.toggleLabel}>
          <input
            type="checkbox"
            checked={filters.medicalOnly}
            onChange={(e) => update('medicalOnly', e.target.checked)}
          />
          <span className={styles.toggleText}>Medical only</span>
        </label>
      </div>
    </div>
  );
}
