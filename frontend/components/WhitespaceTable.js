import { formatCurrency } from '../lib/format';
import styles from './WhitespaceTable.module.css';

export default function WhitespaceTable({ data, loading }) {
  if (loading) {
    return (
      <div className={styles.tableWrap}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th className={styles.th}>#</th>
              <th className={styles.th}>Agency</th>
              <th className={styles.th}>Total Spend</th>
              <th className={styles.th}>Tenders</th>
              <th className={styles.th}>Suppliers</th>
              <th className={styles.th}>Top Competitors</th>
            </tr>
          </thead>
          <tbody>
            {[...Array(5)].map((_, i) => (
              <tr key={i}>
                {[...Array(6)].map((_, j) => (
                  <td key={j} className={styles.td}>
                    <div className="skeleton" style={{ width: '70%', height: 16 }} />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className={styles.tableWrap}>
        <p className={styles.empty}>
          No white-space agencies found — this supplier has coverage across all
          qualifying agencies.
        </p>
      </div>
    );
  }

  return (
    <div className={styles.tableWrap}>
      <table className={styles.table}>
        <thead>
          <tr>
            <th className={styles.th}>#</th>
            <th className={styles.th}>Agency</th>
            <th className={styles.th}>Total Spend</th>
            <th className={styles.th}>Tenders</th>
            <th className={styles.th}>Suppliers</th>
            <th className={styles.th}>Top Competitors</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={i} className={styles.tr}>
              <td className={styles.td}>{i + 1}</td>
              <td className={styles.td}>{row.agency}</td>
              <td className={styles.td}>{formatCurrency(row.total_spend)}</td>
              <td className={styles.td}>{row.num_tenders}</td>
              <td className={styles.td}>{row.num_suppliers}</td>
              <td className={styles.td}>
                <ul className={styles.competitors}>
                  {row.top_competitors?.map((c, j) => (
                    <li key={j}>
                      {c.supplier}{' '}
                      <span className={styles.competitorSpend}>
                        {formatCurrency(c.spend)}
                      </span>
                    </li>
                  ))}
                </ul>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
