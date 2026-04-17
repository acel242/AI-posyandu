import { useState, useEffect } from 'react'
import RiskBadge from '../components/RiskBadge'

export default function KaderDashboard({ user, onLogout }) {
  const [children, setChildren] = useState([])
  const [stats, setStats] = useState({ total: 0, green: 0, yellow: 0, red: 0 })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/children')
      .then(r => r.json())
      .then(data => { setChildren(data); setLoading(false) })
      .catch(() => setLoading(false))

    fetch('/api/stats')
      .then(r => r.json())
      .then(setStats)
      .catch(() => {})
  }, [])

  const cardStyle = (color) => ({
    padding: '14px 12px',
    borderRadius: 12,
    background: color,
    color: 'white',
    textAlign: 'center',
    flex: '1 1 80px',
    minWidth: 80,
  })

  return (
    <div style={{ padding: '1rem', fontFamily: 'system-ui, sans-serif', maxWidth: 900, margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 8, marginBottom: 20 }}>
        <div>
          <h1 style={{ margin: 0, color: '#1a3a2a', fontSize: 20 }}>Dashboard Kader</h1>
          <p style={{ margin: '4px 0 0', color: '#666', fontSize: 13 }}>
            Posyandu Patakbanteng — {user.username}
          </p>
        </div>
        <button onClick={onLogout} style={{ background: 'none', border: 'none', color: '#666', cursor: 'pointer', fontSize: 14, padding: 0 }}>Keluar</button>
      </div>

      {/* Stats Cards */}
      <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginBottom: 20 }}>
        <div style={cardStyle('#22c55e')}>
          <div style={{ fontSize: 28, fontWeight: 'bold' }}>{stats.green}</div>
          <div style={{ fontSize: 13 }}>Normal 🟢</div>
        </div>
        <div style={cardStyle('#eab308')}>
          <div style={{ fontSize: 28, fontWeight: 'bold' }}>{stats.yellow}</div>
          <div style={{ fontSize: 13 }}>Risiko 🟡</div>
        </div>
        <div style={cardStyle('#ef4444')}>
          <div style={{ fontSize: 28, fontWeight: 'bold' }}>{stats.red}</div>
          <div style={{ fontSize: 13 }}>Buruk 🔴</div>
        </div>
        <div style={{ ...cardStyle('#3b82f6'), flex: 1 }}>
          <div style={{ fontSize: 28, fontWeight: 'bold' }}>{stats.total}</div>
          <div style={{ fontSize: 13 }}>Total Anak</div>
        </div>
      </div>

      {/* Children Table */}
      <div style={{ background: 'white', borderRadius: 12, boxShadow: '0 2px 12px rgba(0,0,0,0.06)', overflowX: 'auto' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid #eee' }}>
          <h3 style={{ margin: 0 }}>Daftar Anak</h3>
        </div>

        {loading ? (
          <div style={{ padding: 40, textAlign: 'center', color: '#999' }}>Memuat...</div>
        ) : children.length === 0 ? (
          <div style={{ padding: 40, textAlign: 'center', color: '#999' }}>
            Belum ada data anak. Gunakan /daftar di Telegram Bot untuk mendaftarkan anak.
          </div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
            <thead>
              <tr style={{ background: '#f8fafc' }}>
                <th style={{ padding: '10px 16px', textAlign: 'left', color: '#666', fontWeight: 500 }}>Nama</th>
                <th style={{ padding: '10px 16px', textAlign: 'left', color: '#666', fontWeight: 500 }}>NIK</th>
                <th style={{ padding: '10px 16px', textAlign: 'left', color: '#666', fontWeight: 500 }}>Orang Tua</th>
                <th style={{ padding: '10px 16px', textAlign: 'center', color: '#666', fontWeight: 500 }}>Status</th>
                <th style={{ padding: '10px 16px', textAlign: 'left', color: '#666', fontWeight: 500 }}>Terakhir Posyandu</th>
              </tr>
            </thead>
            <tbody>
              {children.map((child, i) => (
                <tr key={child.id} style={{ borderTop: i > 0 ? '1px solid #f0f0f0' : 'none' }}>
                  <td style={{ padding: '12px 16px' }}>{child.name}</td>
                  <td style={{ padding: '12px 16px', fontFamily: 'monospace', fontSize: 13 }}>{child.nik}</td>
                  <td style={{ padding: '12px 16px' }}>{child.parent_name}</td>
                  <td style={{ padding: '12px 16px', textAlign: 'center' }}>
                    <RiskBadge status={child.risk_status} />
                  </td>
                  <td style={{ padding: '12px 16px', color: '#888', fontSize: 13 }}>
                    {child.last_posyandu_date || '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
