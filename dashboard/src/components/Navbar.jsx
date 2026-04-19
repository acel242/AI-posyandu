import { useState } from 'react'

export default function Navbar({ user, alertFailedCount = 0, onBellClick, onLogout }) {
  return (
    <nav className="navbar">
      <span className="navbar-brand">🏥 Posyandu Connect</span>
      <div className="navbar-spacer" />
      <div className="navbar-actions">
        <span className="navbar-username">{user?.username || 'User'}</span>
        <button className="navbar-badge navbar-btn" onClick={onBellClick} title="Notifikasi">
          🔔
          {alertFailedCount > 0 && (
            <span className="navbar-badge-count">
              {alertFailedCount > 99 ? '99+' : alertFailedCount}
            </span>
          )}
        </button>
        <button className="navbar-btn" onClick={onLogout}>Keluar</button>
      </div>
    </nav>
  )
}
