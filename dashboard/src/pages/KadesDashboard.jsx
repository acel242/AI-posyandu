import { useState, useEffect } from 'react'
import Navbar from '../components/Navbar'
import ChildTable from '../components/ChildTable'
import AlertPanel from '../components/AlertPanel'
import RiskBadge from '../components/RiskBadge'

function formatDateIndonesian() {
  const opts = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }
  return new Date().toLocaleDateString('id-ID', opts)
}

function BarChart({ data, title }) {
  const maxVal = Math.max(...data.map(d => d.value), 1)
  const colors = ['#E74C3C', '#F39C12', '#27AE60']
  return (
    <div className="card">
      <h3 style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: 14 }}>{title}</h3>
      {data.map((item, i) => {
        const pct = Math.round((item.value / maxVal) * 100)
        return (
          <div key={item.label} style={{ marginBottom: 14 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: 4 }}>
              <span>{item.icon} {item.label}</span>
              <span style={{ fontWeight: 700 }}>{item.value} anak ({pct}%)</span>
            </div>
            <div style={{ height: 10, background: '#F0F0F0', borderRadius: 5, overflow: 'hidden' }}>
              <div style={{ width: `${pct}%`, height: '100%', background: colors[i], borderRadius: 5, transition: 'width 0.5s ease' }} />
            </div>
          </div>
        )
      })}
    </div>
  )
}

function StatRing({ label, value, total, color }) {
  const pct = total > 0 ? Math.round((value / total) * 100) : 0
  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{
        width: 72, height: 72, borderRadius: '50%',
        background: `conic-gradient(${color} ${pct}%, #e0e0e0 0%)`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        margin: '0 auto 8px',
        position: 'relative',
      }}>
        <div style={{
          width: 54, height: 54, borderRadius: '50%', background: 'white',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '1.1rem', fontWeight: 700, color: color,
        }}>{value}</div>
      </div>
      <div style={{ fontSize: '0.75rem', color: '#7F8C8D', fontWeight: 500 }}>{label}</div>
    </div>
  )
}

export default function KadesDashboard({ user, onLogout, onBellClick }) {
  const [children, setChildren] = useState([])
  const [stats, setStats] = useState({ total: 0, green: 0, yellow: 0, red: 0, unmeasured: 0 })
  const [alerts, setAlerts] = useState([])
  const [alertStats, setAlertStats] = useState({ sent: 0, failed: 0, pending: 0 })
  const [loading, setLoading] = useState(true)
  const [panelOpen, setPanelOpen] = useState(false)
  const [alertLoading, setAlertLoading] = useState(false)
  const [filter, setFilter] = useState('all')

  useEffect(() => { loadData() }, [])

  async function loadData() {
    setLoading(true)
    try {
      const [c, s] = await Promise.all([
        fetch('/api/children').then(r => r.json()),
        fetch('/api/stats').then(r => r.json()),
      ])
      setChildren(Array.isArray(c) ? c : [])
      setStats(s || {})
    } catch (_) {}
    setLoading(false)
  }

  useEffect(() => {
    if (!panelOpen) return
    setAlertLoading(true)
    Promise.all([
      fetch('/api/alerts/logs?limit=100').then(r => r.json()),
      fetch('/api/alerts/stats').then(r => r.json()),
    ])
      .then(([a, s]) => {
        setAlerts(Array.isArray(a) ? a : [])
        setAlertStats(s || {})
      })
      .catch(() => {})
      .finally(() => setAlertLoading(false))
  }, [panelOpen])

  const handleRetry = async (alertId) => {
    try {
      const r = await fetch(`/api/alerts/retry/${alertId}`, { method: 'POST' })
      const data = await r.json()
      if (data.success) {
        const [a, s] = await Promise.all([
          fetch('/api/alerts/logs?limit=100').then(r => r.json()),
          fetch('/api/alerts/stats').then(r => r.json()),
        ])
        setAlerts(Array.isArray(a) ? a : [])
        setAlertStats(s || {})
      }
    } catch (_) {}
  }

  const filteredChildren = children.filter(c => {
    if (filter === 'normal') return c.risk_status === 'green'
    if (filter === 'risk') return c.risk_status === 'red' || c.risk_status === 'yellow'
    return true
  })

  const chartData = [
    { label: 'Risiko Tinggi', icon: '🔴', value: stats.red || 0 },
    { label: 'Risiko', icon: '🟡', value: stats.yellow || 0 },
    { label: 'Normal', icon: '🟢', value: stats.green || 0 },
  ]

  return (
    <div>
      <Navbar
        user={user}
        alertFailedCount={alertStats.failed || 0}
        onBellClick={() => setPanelOpen(true)}
        onLogout={onLogout}
      />

      <div className="page">
        <div className="page-content">
          {/* Welcome */}
          <div className="welcome-card">
            <h2>Selamat Datang, {user?.username}</h2>
            <p>{formatDateIndonesian()}</p>
          </div>

          {/* Stats ring */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, marginBottom: 20 }}>
            <StatRing label="Normal" value={stats.green || 0} total={stats.total || 1} color="#27AE60" />
            <StatRing label="Risiko" value={stats.yellow || 0} total={stats.total || 1} color="#F39C12" />
            <StatRing label="Rujuk" value={stats.red || 0} total={stats.total || 1} color="#E74C3C" />
          </div>

          {/* Chart */}
          <div style={{ marginBottom: 20 }}>
            <BarChart data={chartData} title="📊 Distribusi Status Gizi" />
          </div>

          {/* Filter */}
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

      <AlertPanel
        isOpen={panelOpen}
        onClose={() => setPanelOpen(false)}
        alerts={alerts}
        stats={alertStats}
        onRetry={handleRetry}
        loading={alertLoading}
      />
    </div>
  )
}
