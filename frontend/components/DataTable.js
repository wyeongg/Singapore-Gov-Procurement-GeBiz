'use client';

import { useState } from 'react';
import styles from './DataTable.module.css';

export default function DataTable({ columns, data, loading }) {
  const [sortKey, setSortKey] = useState(null);
  const [sortDir, setSortDir] = useState('desc');

  const handleSort = (key) => {
    if (sortKey === key) {
      setSortDir(sortDir === 'desc' ? 'asc' : 'desc');
    } else {
      setSortKey(key);
      setSortDir('desc');
    }
  };

  const sorted = data && sortKey
    ? [...data].sort((a, b) => {
        const av = a[sortKey];
        const bv = b[sortKey];
        if (typeof av === 'number' && typeof bv === 'number') {
          return sortDir === 'desc' ? bv - av : av - bv;
        }
        const cmp = String(av).localeCompare(String(bv));
        return sortDir === 'desc' ? -cmp : cmp;
      })
    : data;

  if (loading) {
    return (
      <div className={styles.tableWrap}>
        <table className={styles.table}>
          <thead>
            <tr>
              {columns.map((col) => (
                <th key={col.key} className={styles.th}>{col.label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {[...Array(5)].map((_, i) => (
              <tr key={i}>
                {columns.map((col) => (
                  <td key={col.key} className={styles.td}>
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

  if (!sorted || sorted.length === 0) {
    return (
      <div className={styles.tableWrap}>
        <p className={styles.empty}>No data for current filters</p>
      </div>
    );
  }

  return (
    <div className={styles.tableWrap}>
      <table className={styles.table}>
        <thead>
          <tr>
            <th className={styles.th}>#</th>
            {columns.map((col) => (
              <th
                key={col.key}
                className={styles.th}
                onClick={() => handleSort(col.key)}
                style={{ cursor: 'pointer' }}
              >
                {col.label}
                {sortKey === col.key && (
                  <span className={styles.sortArrow}>
                    {sortDir === 'desc' ? ' \u25BC' : ' \u25B2'}
                  </span>
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sorted.map((row, i) => (
            <tr key={i} className={styles.tr}>
              <td className={styles.td}>{i + 1}</td>
              {columns.map((col) => (
                <td key={col.key} className={styles.td}>
                  {col.format ? col.format(row[col.key]) : row[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
