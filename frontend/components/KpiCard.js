import { useState, useRef, useEffect } from 'react';
import styles from './KpiCard.module.css';

export default function KpiCard({ label, value, loading, tooltip }) {
  const [showTip, setShowTip] = useState(false);
  const tipRef = useRef(null);

  useEffect(() => {
    if (!showTip) return;
    function handleClick(e) {
      if (tipRef.current && !tipRef.current.contains(e.target)) {
        setShowTip(false);
      }
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, [showTip]);

  return (
    <div className={styles.card}>
      <span className={styles.label}>
        {label}
        {tooltip && (
          <span className={styles.tipWrap} ref={tipRef}>
            <button
              className={styles.tipBtn}
              onClick={() => setShowTip(!showTip)}
              aria-label={`Info about ${label}`}
            >
              ?
            </button>
            {showTip && (
              <div className={styles.tipPopover}>{tooltip}</div>
            )}
          </span>
        )}
      </span>
      {loading ? (
        <div className="skeleton" style={{ width: 100, height: 34 }} />
      ) : (
        <span className={styles.value}>{value}</span>
      )}
    </div>
  );
}
