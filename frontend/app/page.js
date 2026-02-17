'use client';

import { useState } from 'react';
import useSWR from 'swr';
import {
  fetcher,
  marketUrl,
  spendOverTimeUrl,
  topAgenciesUrl,
  topSuppliersUrl,
} from '../lib/api';
import { formatCurrency, formatNumber } from '../lib/format';
import KpiCard from '../components/KpiCard';
import FilterBar from '../components/FilterBar';
import SpendChart from '../components/SpendChart';
import DataTable from '../components/DataTable';
import styles from './page.module.css';

const AGENCY_COLUMNS = [
  { key: 'agency', label: 'Agency' },
  { key: 'total_awarded', label: 'Total Awarded', format: formatCurrency },
  { key: 'num_tenders', label: 'Tenders', format: formatNumber },
  { key: 'num_suppliers', label: 'Suppliers', format: formatNumber },
];

const SUPPLIER_COLUMNS = [
  { key: 'supplier', label: 'Supplier' },
  { key: 'total_awarded', label: 'Total Awarded', format: formatCurrency },
  { key: 'num_tenders', label: 'Tenders', format: formatNumber },
  { key: 'num_agencies', label: 'Agencies', format: formatNumber },
];

export default function Dashboard() {
  const [filters, setFilters] = useState({
    medicalOnly: true,
    category: null,
    dateFrom: null,
    dateTo: null,
  });
  const [tableView, setTableView] = useState('agencies');

  const { data: market, isLoading: marketLoading, error: marketError } = useSWR(
    marketUrl(filters),
    fetcher
  );

  const { data: spendData, isLoading: spendLoading } = useSWR(
    spendOverTimeUrl({ ...filters, period: 'monthly' }),
    fetcher
  );

  const { data: agencies, isLoading: agenciesLoading } = useSWR(
    tableView === 'agencies' ? topAgenciesUrl({ ...filters, limit: 10 }) : null,
    fetcher
  );

  const { data: suppliers, isLoading: suppliersLoading } = useSWR(
    tableView === 'suppliers' ? topSuppliersUrl({ ...filters, limit: 10 }) : null,
    fetcher
  );

  return (
    <div className={styles.page}>
      <h1>Medical Procurement Dashboard</h1>

      <FilterBar filters={filters} onChange={setFilters} />

      {marketError && (
        <p className={styles.error}>
          Could not load data. Ensure the API is running at{' '}
          {process.env.NEXT_PUBLIC_API_BASE || 'http://127.0.0.1:8000'}
        </p>
      )}

      <div className={styles.kpiGrid}>
        <KpiCard
          label="Total Spend"
          value={market ? formatCurrency(market.total_awarded) : ''}
          loading={marketLoading}
        />
        <KpiCard
          label="Tenders"
          value={market ? formatNumber(market.num_tenders) : ''}
          loading={marketLoading}
        />
        <KpiCard
          label="Agencies"
          value={market ? formatNumber(market.num_agencies) : ''}
          loading={marketLoading}
        />
        <KpiCard
          label="Suppliers"
          value={market ? formatNumber(market.num_suppliers) : ''}
          loading={marketLoading}
        />
      </div>

      <SpendChart data={spendData} loading={spendLoading} />

      <div>
        <div className={styles.sectionHeader}>
          <h3>
            Top {tableView === 'agencies' ? 'Agencies' : 'Suppliers'}
          </h3>
          <div className={styles.toggle}>
            <button
              className={`${styles.toggleBtn} ${tableView === 'agencies' ? styles.toggleBtnActive : ''}`}
              onClick={() => setTableView('agencies')}
            >
              Agencies
            </button>
            <button
              className={`${styles.toggleBtn} ${tableView === 'suppliers' ? styles.toggleBtnActive : ''}`}
              onClick={() => setTableView('suppliers')}
            >
              Suppliers
            </button>
          </div>
        </div>

        {tableView === 'agencies' ? (
          <DataTable
            columns={AGENCY_COLUMNS}
            data={agencies}
            loading={agenciesLoading}
          />
        ) : (
          <DataTable
            columns={SUPPLIER_COLUMNS}
            data={suppliers}
            loading={suppliersLoading}
          />
        )}
      </div>
    </div>
  );
}
