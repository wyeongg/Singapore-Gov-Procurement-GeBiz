'use client';

import { useState } from 'react';
import styles from './WhitespaceForm.module.css';

const CATEGORIES = [
  { value: '', label: 'All medical' },
  { value: 'diagnostics', label: 'Diagnostics' },
  { value: 'devices', label: 'Devices' },
  { value: 'consumables', label: 'Consumables' },
  { value: 'pharma_biotech', label: 'Pharma / Biotech' },
  { value: 'dental', label: 'Dental' },
  { value: 'services', label: 'Services' },
  { value: 'general', label: 'General Medical' },
];

export default function WhitespaceForm({ onSubmit, supplierSuggestions }) {
  const [supplier, setSupplier] = useState('');
  const [category, setCategory] = useState('');
  const [minSpend, setMinSpend] = useState(100000);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!supplier.trim()) return;
    onSubmit({
      supplier: supplier.trim().toUpperCase(),
      category: category || null,
      minSpend,
    });
  };

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <div className={styles.group}>
        <label className={styles.label}>Supplier name</label>
        <input
          type="text"
          className={styles.input}
          placeholder="e.g. BIOMED DIAGNOSTICS"
          value={supplier}
          onChange={(e) => setSupplier(e.target.value)}
          list="supplier-suggestions"
        />
        {supplierSuggestions && (
          <datalist id="supplier-suggestions">
            {supplierSuggestions.map((s) => (
              <option key={s} value={s} />
            ))}
          </datalist>
        )}
      </div>

      <div className={styles.group}>
        <label className={styles.label}>Category</label>
        <select
          className={styles.input}
          value={category}
          onChange={(e) => setCategory(e.target.value)}
        >
          {CATEGORIES.map((c) => (
            <option key={c.value} value={c.value}>
              {c.label}
            </option>
          ))}
        </select>
      </div>

      <div className={styles.group}>
        <label className={styles.label}>Min spend ($)</label>
        <input
          type="number"
          className={styles.input}
          value={minSpend}
          onChange={(e) => setMinSpend(Number(e.target.value))}
          min={0}
          step={10000}
        />
      </div>

      <button
        type="submit"
        className={styles.button}
        disabled={!supplier.trim()}
      >
        Analyze
      </button>
    </form>
  );
}
