export default function Navbar({ user, alertFailedCount = 0, onBellClick, onLogout }) {
  return (
    <nav style={{
      position: 'fixed',
      top: 0, left: 0, right: 0,
      height: 60,
      background: 'white',
      borderBottom: '1px solid #E5E7EB',
      display: 'flex',
      alignItems: 'center',
      padding: '0 20px',
      zIndex: 100,
    }}>
      <span style={{
        fontWeight: 700,
        fontSize: '1.1rem',
        color: '#0D3B20',
        letterSpacing: '-0.02em',
      }}>
        AI Posyandu
      </span>

      <div style={{ flex: 1 }} />

      <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
        <span style={{
          fontSize: '0.82rem',
          color: '#6B7280',
        }}>
          {user?.username || 'User'}
        </span>

        <button
          onClick={onBellClick}
          style={{
            position: 'relative',
            background: 'none',
            border: '1px solid #E5E7EB',
            borderRadius: 8,
            padding: '7px 10px',
            fontSize: '0.85rem',
            cursor: 'pointer',
            color: '#6B7280',
            transition: 'all 0.15s',
          }}
          onMouseEnter={e => { e.currentTarget.style.background = '#F9FAFB'; e.currentTarget.style.borderColor = '#D1D5DB' }}
          onMouseLeave={e => { e.currentTarget.style.background = 'none'; e.currentTarget.style.borderColor = '#E5E7EB' }}
          title="Notifikasi"
        >
          🔔
          {alertFailedCount > 0 && (
            <span style={{
              position: 'absolute',
              top: -4, right: -4,
              background: '#EF4444',
              color: 'white',
              fontSize: '0.6rem',
              fontWeight: 700,
              width: 16, height: 16,
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: '2px solid white',
            }}>
              {alertFailedCount > 9 ? '9+' : alertFailedCount}
            </span>
          )}
        </button>

        <button
          onClick={onLogout}
          style={{
            background: 'none',
            border: '1px solid #E5E7EB',
            borderRadius: 8,
            padding: '7px 14px',
            fontSize: '0.82rem',
            fontWeight: 500,
            color: '#6B7280',
            cursor: 'pointer',
            transition: 'all 0.15s',
          }}
          onMouseEnter={e => { e.currentTarget.style.background = '#FEF2F2'; e.currentTarget.style.borderColor = '#FECACA'; e.currentTarget.style.color = '#991B1B' }}
          onMouseLeave={e => { e.currentTarget.style.background = 'none'; e.currentTarget.style.borderColor = '#E5E7EB'; e.currentTarget.style.color = '#6B7280' }}
        >
          Keluar
        </button>
      </div>
    </nav>
  )
}
