'use client';

import { Inter } from 'next/font/google';
import Link from 'next/link';
import { usePathname, useSearchParams } from 'next/navigation';
import { Suspense } from 'react';
import './globals.css';
import styles from './layout.module.css';

const inter = Inter({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
  display: 'swap',
});

function NavBar() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const embed = searchParams.get('embed') === 'true';

  if (embed) return null;

  return (
    <nav className={styles.nav}>
      <span className={styles.navTitle}>GeBIZ Medical Analytics</span>
      <div className={styles.navLinks}>
        <Link
          href="/"
          className={`${styles.navLink} ${pathname === '/' ? styles.navLinkActive : ''}`}
        >
          Dashboard
        </Link>
        <Link
          href="/whitespace"
          className={`${styles.navLink} ${pathname === '/whitespace' ? styles.navLinkActive : ''}`}
        >
          White Space
        </Link>
      </div>
    </nav>
  );
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Suspense>
          <NavBar />
        </Suspense>
        <main className={styles.container}>{children}</main>
      </body>
    </html>
  );
}
