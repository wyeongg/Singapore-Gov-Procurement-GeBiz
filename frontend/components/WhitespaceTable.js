import { formatCurrency } from '../lib/format';
import styles from './WhitespaceTable.module.css';

const HEADERS = [
  '#',
  'Agency',
  'Total Spend',
  'Tenders',
  'Suppliers',
  'Top Competitors',
  'Top Tenders (by $)',
  'Top Tenders (by Count)',
];

function TenderList({ items, mode }) {
  if (!items || items.length === 0) return <span className={styles.muted}>—</span>;
  return (
    <ul className={styles.nestedList}>
      {items.map((t, i) => (
        <li key={i} title={t.description}>
          <span className={styles.tenderDesc}>{t.description}</span>{' '}
          <span className={styles.tenderMeta}>
            {mode === 'value' ? formatCurrency(t.total_value) : `${t.count}x`}
          </span>
        </li>
      ))}
    </ul>
  );
}

export default function WhitespaceTable({ data, loading }) {
  if (loading) {
    return (
      <div className={styles.tableWrap}>
        <table className={styles.table}>
          <thead>
            <tr>
              {HEADERS.map((h) => (
                <th key={h} className={styles.th}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {[...Array(5)].map((_, i) => (
              <tr key={i}>
                {HEADERS.map((_, j) => (
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
            {HEADERS.map((h) => (
              <th key={h} className={styles.th}>{h}</th>
            ))}
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
              <td className={styles.td}>
                <TenderList items={row.top_tenders_by_value} mode="value" />
              </td>
              <td className={styles.td}>
                <TenderList items={row.top_tenders_by_count} mode="count" />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
