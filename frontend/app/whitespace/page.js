'use client';

import { useState } from 'react';
import useSWR from 'swr';
import { fetcher, whitespaceUrl, topSuppliersUrl } from '../../lib/api';
import { formatCurrency, formatNumber, formatPercent } from '../../lib/format';
import KpiCard from '../../components/KpiCard';
import WhitespaceForm from '../../components/WhitespaceForm';
import WhitespaceTable from '../../components/WhitespaceTable';
import styles from './page.module.css';

const WS_TOOLTIPS = {
  agencies:
    'Number of agencies that spend in this category but have never awarded a tender to the selected supplier.',
  spend:
    'Total dollar value of tenders from white-space agencies. This is the addressable market the supplier is currently missing.',
  share:
    'White-space spend as a percentage of total category spend. 100% means the supplier has zero awards in this category — all spend is untapped.',
};

export default function WhitespacePage() {
  const [wsParams, setWsParams] = useState(null);

  const { data: topSuppliers } = useSWR(
    topSuppliersUrl({ limit: 100 }),
    fetcher
  );

  const supplierNames = topSuppliers
    ? topSuppliers.map((s) => s.supplier)
    : null;

  const { data: wsData, isLoading: wsLoading, error: wsError } = useSWR(
    wsParams ? whitespaceUrl(wsParams) : null,
    fetcher
  );

  const handleSubmit = (params) => {
    setWsParams(params);
  };

  return (
    <div className={styles.page}>
      <h1>White-Space Analysis</h1>
      <p style={{ color: 'var(--color-text-secondary)', marginTop: -16 }}>
        Find agencies that spend in a category but have not awarded to a specific supplier.
      </p>

      <WhitespaceForm
        onSubmit={handleSubmit}
        supplierSuggestions={supplierNames}
      />

      {wsError && (
        <p className={styles.error}>
          Could not load white-space data. Check the supplier name and ensure the
          API is running.
        </p>
      )}

      {wsData && (
        <>
          <div className={styles.kpiGrid}>
            <KpiCard
              label="White-Space Agencies"
              value={formatNumber(wsData.summary.num_whitespace_agencies)}
              loading={wsLoading}
              tooltip={WS_TOOLTIPS.agencies}
            />
            <KpiCard
              label="White-Space Spend"
              value={formatCurrency(wsData.summary.whitespace_total_spend)}
              loading={wsLoading}
              tooltip={WS_TOOLTIPS.spend}
            />
            <KpiCard
              label="Share of Category"
              value={formatPercent(wsData.summary.whitespace_share_pct)}
              loading={wsLoading}
              tooltip={WS_TOOLTIPS.share}
            />
          </div>

          <div>
            <h3 style={{ marginBottom: 12 }}>
              White-Space Agencies for {wsData.supplier}
              {wsData.category ? ` (${wsData.category})` : ''}
            </h3>
            <WhitespaceTable data={wsData.agencies} loading={wsLoading} />
          </div>
        </>
      )}
    </div>
  );
}
