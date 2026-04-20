import { useState, useEffect } from 'react'
import Navbar from '../components/Navbar'
import ChildTable from '../components/ChildTable'
import ChildForm from '../components/ChildForm'
import StatCard from '../components/StatCard'
import WarningCard from '../components/WarningCard'

function formatDateIndonesian() {
  const opts = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }
  return new Date().toLocaleDateString('id-ID', opts)
}

export default function KaderDashboard({ user, onLogout, onBellClick }) {
  const navigate = useNavigate()
  const [children, setChildren] = useState([])
  const [stats, setStats] = useState({ total: 0, normal: 0, risk: 0, unmeasured: 0 })
  const [alerts, setAlerts] = useState({ total: 0, sent: 0, failed: 0, pending: 0 })
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all') // all | normal | risk
  const [showForm, setShowForm] = useState(false)
  const [editChild, setEditChild] = useState(null)

  useEffect(() => {
    loadData()
  }, [])

  async function loadData() {
    setLoading(true)
    try {
      const [childrenRes, statsRes, alertsRes] = await Promise.all([
        fetch('/api/children'),
        fetch('/api/stats'),
        fetch('/api/alerts/stats'),
      ])
      const childrenData = await childrenRes.json()
      const statsData = await statsRes.json()
      const alertsData = await alertsRes.json()
      setChildren(Array.isArray(childrenData) ? childrenData : [])
      setStats(statsData)
      setAlerts(alertsData)
    } catch (err) {
      console.error('Failed to load data:', err)
    } finally {
      setLoading(false)
    }
  }

  async function handleAddChild(formData) {
    const res = await fetch('/api/children', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData),
    })
    const data = await res.json()
    if (data.success || data.id) {
      setShowForm(false)
      loadData()
    } else {
      alert('Gagal menyimpan: ' + (data.error || 'Unknown error'))
    }
  }

  async function handleDeleteChild(id) {
    if (!confirm('Yakin hapus data anak ini?')) return
    await fetch(`/api/children/${id}`, { method: 'DELETE' })
    loadData()
  }

  function handleEditChild(child) {
    setEditChild(child)
    setShowForm(true)
  }

  function handleRowClick(child) {
    setEditChild(child)
    setShowForm(true)
  }

  const filteredChildren = children.filter(c => {
    if (filter === 'normal') return c.risk_status === 'green'
    if (filter === 'risk') return c.risk_status === 'red' || c.risk_status === 'yellow'
    return true
  })

  return (
    <div>
      <Navbar
        user={user}
        alertFailedCount={alerts.failed || 0}
        onBellClick={onBellClick}
        onLogout={onLogout}
      />

      <div className="page">
        <div className="page-content">
          {/* Welcome */}
          <div className="welcome-card">
            <h2>Selamat Datang, {user?.username}</h2>
            <p>{formatDateIndonesian()}</p>
          </div>

          {/* Warning: children >30 days unmeasured */}
          <WarningCard count={stats.unmeasured || 0} />

          {/* Stats */}
          <div className="stats-grid">
            <StatCard
              icon="👶"
              label="Total Anak"
              value={stats.total || 0}
              variant="total"
            />
            <StatCard
              icon="✅"
              label="Normal"
              value={stats.normal || 0}
              variant="normal"
            />
            <StatCard
              icon="⚠️"
              label="Berisiko"
              value={(stats.risk || 0) + (stats.yellow || 0)}
              variant="risk"
            />
          </div>

          {/* Child Table */}
          <div className="section-header">
            <span className="section-title">📋 Data Anak</span>
            <div className="filter-bar">
              <button
                className={`filter-chip ${filter === 'all' ? 'active' : ''}`}
                onClick={() => setFilter('all')}
              >Semua</button>
              <button
                className={`filter-chip ${filter === 'normal' ? 'active' : ''}`}
                onClick={() => setFilter('normal')}
              >Normal</button>
              <button
                className={`filter-chip ${filter === 'risk' ? 'active' : ''}`}
                onClick={() => setFilter('risk')}
              >Berisiko</button>
            </div>
          </div>

          {loading ? (
            <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
              Memuat data...
            </div>
          ) : (
            <ChildTable
              children={filteredChildren}
              onRowClick={handleRowClick}
              onDelete={handleDeleteChild}
              onChartClick={child => navigate(`/child/${child.id}`)}
            />
          )}
        </div>
      </div>

      {/* FAB */}
      <button className="fab" onClick={() => { setEditChild(null); setShowForm(true) }} title="Tambah Anak">
        +
      </button>

      {/* Child Form Modal */}
      {showForm && (
        <ChildForm
          child={editChild}
          onSave={handleAddChild}
          onClose={() => { setShowForm(false); setEditChild(null) }}
        />
      )}
    </div>
  )
}
