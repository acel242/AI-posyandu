/**
 * AlertBadge — notification bell with unread count badge.
 * Props:
 *   count   — number of unread/failed alerts
 *   onClick — callback when bell is clicked
 */
export default function AlertBadge({ count, onClick }) {
  return (
    <button
      onClick={onClick}
      style={{
        position: 'relative',
        background: 'none',
        border: 'none',
        cursor: 'pointer',
        fontSize: 20,
        padding: '4px 8px',
        borderRadius: 8,
        transition: 'background 0.15s',
      }}
      title="Notifikasi"
      onMouseEnter={e => e.currentTarget.style.background = '#f0f0f0'}
      onMouseLeave={e => e.currentTarget.style.background = 'none'}
    >
      🔔
      {count > 0 && (
        <span style={{
          position: 'absolute',
          top: 0,
          right: 0,
          background: '#ef4444',
          color: '#fff',
          borderRadius: '50%',
          fontSize: 10,
          fontWeight: 700,
          minWidth: 16,
          height: 16,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '0 3px',
          lineHeight: 1,
          fontFamily: 'system-ui, sans-serif',
        }}>
          {count > 99 ? '99+' : count}
        </span>
      )}
    </button>
  )
}
