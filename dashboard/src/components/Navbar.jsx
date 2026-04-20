export default function Navbar({ user, alertFailedCount = 0, onBellClick, onLogout }) {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <div className="navbar-brand-icon">AI</div>
        <span>AI Posyandu</span>
      </div>

      <div className="navbar-spacer" />

      <div className="navbar-actions">
        <span className="navbar-username">{user?.username || 'User'}</span>

        {onBellClick && (
          <button
            className="navbar-icon-btn"
            onClick={onBellClick}
            title="Notifikasi"
          >
            🔔
            {alertFailedCount > 0 && (
              <span className="navbar-badge">
                {alertFailedCount > 9 ? '9+' : alertFailedCount}
              </span>
            )}
          </button>
        )}

        {onLogout && (
          <button className="navbar-logout-btn" onClick={onLogout}>
            <span>🚪</span>
            <span>Keluar</span>
          </button>
        )}
      </div>
    </nav>
  )
}
