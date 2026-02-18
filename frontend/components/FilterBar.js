import styles from './FilterBar.module.css';

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
    </div>
  );
}
