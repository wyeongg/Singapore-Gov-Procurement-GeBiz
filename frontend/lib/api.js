const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://127.0.0.1:8000';

export async function fetcher(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

function buildUrl(path, params) {
  const url = new URL(path, API_BASE);
  Object.entries(params).forEach(([key, value]) => {
    if (value != null && value !== '') {
      url.searchParams.set(key, String(value));
    }
  });
  return url.toString();
}

export function marketUrl({ medicalOnly = true, category, dateFrom, dateTo } = {}) {
  return buildUrl('/summary/market', {
    medical_only: medicalOnly,
    category,
    date_from: dateFrom,
    date_to: dateTo,
  });
}

export function spendOverTimeUrl({
  period = 'monthly',
  medicalOnly = true,
  category,
  dateFrom,
  dateTo,
  agency,
} = {}) {
  return buildUrl('/summary/spend-over-time', {
    period,
    medical_only: medicalOnly,
    category,
    date_from: dateFrom,
    date_to: dateTo,
    agency,
  });
}

export function topAgenciesUrl({
  limit = 10,
  medicalOnly = true,
  category,
  dateFrom,
  dateTo,
} = {}) {
  return buildUrl('/summary/top-agencies', {
    limit,
    medical_only: medicalOnly,
    category,
    date_from: dateFrom,
    date_to: dateTo,
  });
}

export function topSuppliersUrl({
  limit = 10,
  medicalOnly = true,
  category,
  dateFrom,
  dateTo,
  agency,
} = {}) {
  return buildUrl('/summary/top-suppliers', {
    limit,
    medical_only: medicalOnly,
    category,
    date_from: dateFrom,
    date_to: dateTo,
    agency,
  });
}

export function subcategoriesUrl({ dateFrom, dateTo, agency } = {}) {
  return buildUrl('/summary/subcategories', {
    date_from: dateFrom,
    date_to: dateTo,
    agency,
  });
}

export function tendersUrl({
  keyword,
  limit = 50,
  medicalOnly = true,
  category,
  dateFrom,
  dateTo,
  agency,
  supplier,
  minAmount,
} = {}) {
  return buildUrl('/tenders', {
    keyword,
    limit,
    medical_only: medicalOnly,
    category,
    date_from: dateFrom,
    date_to: dateTo,
    agency,
    supplier,
    min_amount: minAmount,
  });
}

export function whitespaceUrl({
  supplier,
  category,
  dateFrom,
  dateTo,
  minSpend = 100000,
  limit = 50,
} = {}) {
  return buildUrl('/whitespace/agencies', {
    supplier,
    category,
    date_from: dateFrom,
    date_to: dateTo,
    min_spend: minSpend,
    limit,
  });
}
