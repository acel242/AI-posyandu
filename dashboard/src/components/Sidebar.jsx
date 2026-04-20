import { useState } from 'react'

const NAV_ITEMS = [
  { icon: '🏠', label: 'Dashboard', path: '/' },
  { icon: '👶', label: 'Data Anak', path: '/children' },
  { icon: '📅', label: 'Jadwal', path: '/schedules' },
  { icon: '🔔', label: 'Notifikasi', path: '/notifications' },
  { icon: '⚙️', label: 'Pengaturan', path: '/settings' },
]

export default function Sidebar({ user, activePath = '/', onNavigate, onLogout, alertFailedCount = 0 }) {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <div style={{
      display: 'flex',
      minHeight: '100vh',
      background: 'var(--color-bg)',
    }}>
      {/* Sidebar */}
      <aside style={{
        width: collapsed ? 68 : 240,
        background: '#1B5E20',
        color: 'white',
        display: 'flex',
        flexDirection: 'column',
        transition: 'width 0.2s ease',
        flexShrink: 0,
        position: 'fixed',
        top: 0,
        left: 0,
        bottom: 0,
        zIndex: 100,
        overflow: 'hidden',
      }}>
        {/* Logo */}
        <div style={{
          padding: collapsed ? '20px 0' : '20px 20px',
          borderBottom: '1px solid rgba(255,255,255,0.1)',
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          justifyContent: collapsed ? 'center' : 'flex-start',
        }}>
          <span style={{ fontSize: '1.5rem' }}>🏥</span>
          {!collapsed && (
            <div>
              <div style={{ fontWeight: 700, fontSize: '1rem', lineHeight: 1.2 }}>AI Posyandu</div>
              <div style={{ fontSize: '0.7rem', opacity: 0.7 }}>Sistem Cerdas</div>
            </div>
          )}
        </div>

        {/* Nav */}
        <nav style={{ flex: 1, padding: '12px 8px' }}>
          {NAV_ITEMS.map(item => {
            const active = activePath === item.path || (item.path !== '/' && activePath.startsWith(item.path))
            return (
              <button
                key={item.path}
                onClick={() => onNavigate && onNavigate(item.path)}
                style={{
                  width: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 12,
                  padding: collapsed ? '12px 0' : '12px 14px',
                  justifyContent: collapsed ? 'center' : 'flex-start',
                  marginBottom: 4,
                  borderRadius: 10,
                  border: 'none',
                  background: active ? 'rgba(255,255,255,0.15)' : 'transparent',
                  color: 'white',
                  fontSize: '0.875rem',
                  fontWeight: active ? 600 : 400,
                  cursor: 'pointer',
                  transition: 'background 0.15s',
                  textAlign: 'left',
                }}
                onMouseEnter={e => { if (!active) e.currentTarget.style.background = 'rgba(255,255,255,0.08)' }}
                onMouseLeave={e => { if (!active) e.currentTarget.style.background = 'transparent' }}
              >
                <span style={{ fontSize: '1.1rem', flexShrink: 0 }}>{item.icon}</span>
                {!collapsed && <span>{item.label}</span>}
                {item.path === '/notifications' && alertFailedCount > 0 && (
                  <span style={{
                    marginLeft: 'auto',
                    background: '#E74C3C',
                    color: 'white',
                    fontSize: '0.65rem',
                    fontWeight: 700,
                    borderRadius: 10,
                    padding: '2px 6px',
                    minWidth: 18,
                    textAlign: 'center',
                  }}>
                    {alertFailedCount > 99 ? '99+' : alertFailedCount}
                  </span>
                )}
              </button>
            )
          })}
        </nav>

        {/* Bottom */}
        <div style={{
          padding: '12px 8px',
          borderTop: '1px solid rgba(255,255,255,0.1)',
        }}>
          {/* Collapse toggle */}
          <button
            onClick={() => setCollapsed(c => !c)}
            style={{
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              gap: 12,
              padding: collapsed ? '10px 0' : '10px 14px',
              justifyContent: collapsed ? 'center' : 'flex-start',
              marginBottom: 8,
              borderRadius: 10,
              border: 'none',
              background: 'transparent',
              color: 'rgba(255,255,255,0.6)',
              fontSize: '0.8rem',
              cursor: 'pointer',
            }}
          >
            <span style={{ fontSize: '1rem' }}>{collapsed ? '→' : '←'}</span>
            {!collapsed && <span>Collapse</span>}
          </button>

          {/* User */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 10,
            padding: collapsed ? '10px 0' : '10px 14px',
            justifyContent: collapsed ? 'center' : 'flex-start',
          }}>
            <div style={{
              width: 34,
              height: 34,
              borderRadius: '50%',
              background: 'rgba(255,255,255,0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '0.9rem',
              flexShrink: 0,
            }}>
              👤
            </div>
            {!collapsed && (
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontWeight: 600, fontSize: '0.85rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {user?.username || 'User'}
                </div>
                <div style={{ fontSize: '0.7rem', opacity: 0.6, textTransform: 'capitalize' }}>{user?.role || 'kader'}</div>
              </div>
            )}
            {!collapsed && (
              <button
                onClick={onLogout}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'rgba(255,255,255,0.5)',
                  cursor: 'pointer',
                  fontSize: '0.8rem',
                  padding: 4,
                }}
                title="Keluar"
              >
                🚪
              </button>
            )}
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main style={{
        flex: 1,
        marginLeft: collapsed ? 68 : 240,
        transition: 'margin-left 0.2s ease',
        minHeight: '100vh',
      }}>
        {/* Top bar */}
        <header style={{
          background: 'white',
          borderBottom: '1px solid var(--color-border)',
          padding: '0 24px',
          height: 60,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          position: 'sticky',
          top: 0,
          zIndex: 50,
        }}>
          <div style={{ fontSize: '0.85rem', color: 'var(--color-text-light)' }}>
            {NAV_ITEMS.find(n => activePath === n.path || (n.path !== '/' && activePath.startsWith(n.path)))?.label || 'Dashboard'}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--color-text-light)' }}>
              {new Date().toLocaleDateString('id-ID', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
            </span>
          </div>
        </header>

        {/* Page content */}
        <div style={{ padding: 24 }}>
          {/* children slot */}
        </div>
      </main>
    </div>
  )
}
