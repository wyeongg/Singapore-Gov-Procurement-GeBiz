import styles from './KpiCard.module.css';

export default function KpiCard({ label, value, loading }) {
  return (
    <div className={styles.card}>
      <span className={styles.label}>{label}</span>
      {loading ? (
        <div className="skeleton" style={{ width: 100, height: 34 }} />
      ) : (
        <span className={styles.value}>{value}</span>
      )}
    </div>
  );
}
