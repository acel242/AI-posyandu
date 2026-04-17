import { useState, useEffect } from 'react'
import RiskBadge from '../components/RiskBadge'

export default function KepalaDesaDashboard({ user }) {
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

  // Simple text-based bar chart
  const StatBar = ({ label, value, total, color }) => {
    const pct = total > 0 ? Math.round((value / total) * 100) : 0
    return (
      <div style={{ marginBottom: 12 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 14, marginBottom: 4 }}>
          <span>{label}</span>
          <span style={{ fontWeight: 'bold' }}>{value} ({pct}%)</span>
        </div>
        <div style={{ background: '#e5e7eb', borderRadius: 6, height: 12, overflow: 'hidden' }}>
          <div style={{ background: color, height: '100%', width: `${pct}%`, transition: 'width 0.5s' }} />
        </div>
      </div>
    )
  }

  return (
    <div style={{ padding: '1.5rem', fontFamily: 'system-ui, sans-serif', maxWidth: 900, margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <h1 style={{ margin: 0, color: '#1a3a2a' }}>Dashboard Kepala Desa</h1>
          <p style={{ margin: '4px 0 0', color: '#666', fontSize: 14 }}>
            Desa Patakbanteng — {user.username}
          </p>
        </div>
        <a href="/login" style={{ color: '#666', textDecoration: 'none', fontSize: 14 }}>Keluar</a>
      </div>

      {/* Village Summary */}
      <div style={{ background: 'white', borderRadius: 12, padding: 20, boxShadow: '0 2px 12px rgba(0,0,0,0.06)', marginBottom: 20 }}>
        <h3 style={{ margin: '0 0 16px', color: '#1a3a2a' }}>📊 Ringkasan Kesehatan Anak Desa</h3>
        {loading ? (
          <div style={{ color: '#999' }}>Memuat...</div>
        ) : (
          <>
            <StatBar label="🟢 Normal" value={stats.green} total={stats.total} color="#22c55e" />
            <StatBar label="🟡 Risiko" value={stats.yellow} total={stats.total} color="#eab308" />
            <StatBar label="🔴 Buruk" value={stats.red} total={stats.total} color="#ef4444" />
          </>
        )}
      </div>

      {/* Quick Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }}>
        <div style={{ background: 'white', borderRadius: 12, padding: 20, boxShadow: '0 2px 12px rgba(0,0,0,0.06)', textAlign: 'center' }}>
          <div style={{ fontSize: 40, fontWeight: 'bold', color: '#2d7a4f' }}>{stats.total}</div>
          <div style={{ color: '#666', fontSize: 14 }}>Total Anak Terdaftar</div>
        </div>
        <div style={{ background: '#fef2f2', borderRadius: 12, padding: 20, boxShadow: '0 2px 12px rgba(0,0,0,0.06)', textAlign: 'center' }}>
          <div style={{ fontSize: 40, fontWeight: 'bold', color: '#ef4444' }}>{stats.red}</div>
          <div style={{ color: '#666', fontSize: 14 }}>Butuh Rujukan Segera</div>
        </div>
      </div>

      {/* Export placeholder */}
      <div style={{ background: 'white', borderRadius: 12, padding: 20, boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}>
        <h3 style={{ margin: '0 0 12px', color: '#1a3a2a' }}>📋 Laporan</h3>
        <p style={{ color: '#666', margin: '0 0 12px', fontSize: 14 }}>
          Fitur export laporan untuk pemerintah desa sedang dalam pengembangan.
        </p>
        <button
          onClick={() => alert('Fitur export akan segera ditambahkan')}
          style={{
            background: '#2d7a4f', color: 'white', border: 'none',
            padding: '10px 20px', borderRadius: 8, cursor: 'pointer', fontSize: 14
          }}
        >
          Export Laporan (Segera)
        </button>
      </div>
    </div>
  )
}
