import { useState, useEffect } from 'react'
import Navbar from '../components/Navbar'
import ChildTable from '../components/ChildTable'
import StatCard from '../components/StatCard'

function formatDateIndonesian() {
  const opts = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }
  return new Date().toLocaleDateString('id-ID', opts)
}

export default function KepalaDesaDashboard({ user, onLogout, onBellClick }) {
  const [children, setChildren] = useState([])
  const [stats, setStats] = useState({ total: 0, green: 0, yellow: 0, red: 0, unmeasured: 0 })
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    Promise.all([
      fetch('/api/children').then(r => r.json()),
      fetch('/api/stats').then(r => r.json()),
    ])
      .then(([c, s]) => {
        setChildren(Array.isArray(c) ? c : [])
        setStats(s || {})
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  const filteredChildren = children.filter(c => {
    if (filter === 'normal') return c.risk_status === 'green'
    if (filter === 'risk') return c.risk_status === 'red' || c.risk_status === 'yellow'
    return true
  })

  return (
    <div>
      <Navbar user={user} alertFailedCount={0} onBellClick={onBellClick} onLogout={onLogout} />
      <div className="page">
        <div className="page-content">
          <div className="welcome-card">
            <h2>Selamat Datang, {user?.username}</h2>
            <p>{formatDateIndonesian()}</p>
          </div>
          <div className="stats-grid">
            <StatCard icon="👶" label="Total Anak" value={stats.total || 0} variant="total" />
            <StatCard icon="🟢" label="Normal" value={stats.green || 0} variant="normal" />
            <StatCard icon="🔴" label="Rujuk" value={stats.red || 0} variant="risk" />
          </div>
          <div className="section-header">
            <span className="section-title">📋 Data Anak</span>
            <div className="filter-bar">
              <button className={`filter-chip ${filter === 'all' ? 'active' : ''}`} onClick={() => setFilter('all')}>Semua</button>
              <button className={`filter-chip ${filter === 'normal' ? 'active' : ''}`} onClick={() => setFilter('normal')}>Normal</button>
              <button className={`filter-chip ${filter === 'risk' ? 'active' : ''}`} onClick={() => setFilter('risk')}>Berisiko</button>
            </div>
          </div>
          {loading ? (
            <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>Memuat...</div>
          ) : (
            <ChildTable children={filteredChildren} onRowClick={() => {}} onDelete={null} />
          )}
        </div>
      </div>
    </div>
  )
}
