import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import ChildTable from '../components/ChildTable'
import ChildForm from '../components/ChildForm'
import StatCard from '../components/StatCard'
import WarningCard from '../components/WarningCard'
import SchedulePanel from '../components/SchedulePanel'

function StatBox({ icon, label, value, color = '#1B5E20' }) {
  return (
    <div style={{
      background: 'white',
      borderRadius: 16,
      padding: '20px 24px',
      display: 'flex',
      alignItems: 'center',
      gap: 16,
      boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
      flex: 1,
      minWidth: 160,
    }}>
      <div style={{
        width: 52, height: 52,
        borderRadius: 14,
        background: color + '15',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: '1.4rem',
        flexShrink: 0,
      }}>
        {icon}
      </div>
      <div>
        <div style={{ fontSize: '0.75rem', color: '#7F8C8D', marginBottom: 2, fontWeight: 500 }}>{label}</div>
        <div style={{ fontSize: '1.6rem', fontWeight: 700, color: '#2C3E50', lineHeight: 1 }}>{value}</div>
      </div>
    </div>
  )
}

function filterChildren(children, filter) {
  if (filter === 'normal') return children.filter(c => c.risk_status === 'green')
  if (filter === 'risk') return children.filter(c => c.risk_status === 'red' || c.risk_status === 'yellow')
  return children
}

export default function KaderDashboard({ user, onLogout, onBellClick }) {
  const navigate = useNavigate()
  const [children, setChildren] = useState([])
  const [stats, setStats] = useState({ total: 0, normal: 0, risk: 0, unmeasured: 0, yellow: 0 })
  const [alerts, setAlerts] = useState({ total: 0, sent: 0, failed: 0, pending: 0 })
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')
  const [showForm, setShowForm] = useState(false)
  const [editChild, setEditChild] = useState(null)
  const [showSchedule, setShowSchedule] = useState(false)
  const [activeNav, setActiveNav] = useState('/')

  useEffect(() => { loadData() }, [])
  useEffect(() => {
    const loadAlerts = async () => {
      try {
        const r = await fetch('/api/alerts/stats')
        const d = await r.json()
        setAlerts(d)
      } catch {}
    }
    loadAlerts()
  }, [])

  async function loadData() {
    setLoading(true)
    try {
      const [cr, sr] = await Promise.all([fetch('/api/children'), fetch('/api/stats')])
      const cd = await cr.json()
      const sd = await sr.json()
      setChildren(Array.isArray(cd) ? cd : [])
      setStats(sd)
    } catch {}
    setLoading(false)
  }

  async function handleSave(formData) {
    const res = await fetch('/api/children', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData),
    })
    const data = await res.json()
    if (data.success || data.id) { setShowForm(false); loadData() }
    else alert('Gagal: ' + (data.error || 'unknown'))
  }

  async function handleDelete(id) {
    if (!confirm('Hapus data anak ini?')) return
    await fetch(`/api/children/${id}`, { method: 'DELETE' })
    loadData()
  }

  const filtered = filterChildren(children, filter)
  const riskCount = (stats.risk || 0) + (stats.yellow || 0)

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#F5F6FA' }}>
      <Sidebar
        user={user}
        activePath={activeNav}
        onNavigate={p => { setActiveNav(p); if (p === '/schedules') setShowSchedule(true) }}
        onLogout={onLogout}
        alertFailedCount={alerts.failed || 0}
      />

      {/* Main Content */}
      <div style={{ flex: 1, marginLeft: 240, transition: 'margin-left 0.2s' }}>
        {/* Header */}
        <div style={{
          background: 'white',
          borderBottom: '1px solid #E0E4E8',
          padding: '0 28px',
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}>
          <div>
            <h1 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#2C3E50' }}>
              {activeNav === '/schedules' ? '📅 Jadwal Posyandu' : '🏠 Dashboard'}
            </h1>
            <p style={{ fontSize: '0.75rem', color: '#7F8C8D' }}>
              {new Date().toLocaleDateString('id-ID', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
            </p>
          </div>
          <div style={{ display: 'flex', gap: 10 }}>
            <button
              onClick={() => setShowSchedule(true)}
              style={{
                display: 'flex', alignItems: 'center', gap: 6,
                padding: '8px 16px',
                borderRadius: 10,
                border: '1.5px solid #E0E4E8',
                background: 'white',
                fontSize: '0.85rem',
                fontWeight: 500,
                cursor: 'pointer',
                color: '#2C3E50',
              }}
            >
              📅 Atur Jadwal
            </button>
            <button
              onClick={() => { setEditChild(null); setShowForm(true) }}
              style={{
                display: 'flex', alignItems: 'center', gap: 6,
                padding: '8px 20px',
                borderRadius: 10,
                border: 'none',
                background: '#1B5E20',
                fontSize: '0.85rem',
                fontWeight: 600,
                cursor: 'pointer',
                color: 'white',
              }}
            >
              + Tambah Anak
            </button>
          </div>
        </div>

        {/* Content */}
        <div style={{ padding: '24px 28px' }}>
          {activeNav !== '/schedules' && (
            <>
              {/* Welcome */}
              <div style={{
                background: 'linear-gradient(135deg, #1B5E20 0%, #2E7D32 50%, #388E3C 100%)',
                borderRadius: 20,
                padding: '24px 28px',
                color: 'white',
                marginBottom: 20,
                position: 'relative',
                overflow: 'hidden',
              }}>
                <div style={{
                  position: 'absolute', right: -20, top: -20,
                  width: 140, height: 140,
                  borderRadius: '50%',
                  background: 'rgba(255,255,255,0.06)',
                }} />
                <div style={{
                  position: 'absolute', right: 60, bottom: -30,
                  width: 80, height: 80,
                  borderRadius: '50%',
                  background: 'rgba(255,255,255,0.04)',
                }} />
                <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: 4 }}>
                  Selamat Datang, {user?.username || 'Kader'} 👋
                </h2>
                <p style={{ opacity: 0.8, fontSize: '0.875rem' }}>
                  {stats.total > 0
                    ? `Kamu mengelola ${stats.total} anak di Posyandu ini`
                    : 'Belum ada data anak. Tambahkan anak pertama!'}
                </p>
              </div>

              {/* Warning */}
              <WarningCard count={stats.unmeasured || 0} />

              {/* Stats */}
              <div style={{ display: 'flex', gap: 12, marginBottom: 24, flexWrap: 'wrap' }}>
                <StatBox icon="👶" label="Total Anak" value={stats.total || 0} color="#1B5E20" />
                <StatBox icon="✅" label="Normal" value={stats.normal || 0} color="#2E7D32" />
                <StatBox icon="⚠️" label="Berisiko" value={riskCount} color="#F57C00" />
              </div>

              {/* Table section */}
              <div style={{ background: 'white', borderRadius: 16, boxShadow: '0 1px 3px rgba(0,0,0,0.08)', overflow: 'hidden' }}>
                <div style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  padding: '16px 20px',
                  borderBottom: '1px solid #F0F0F0',
                }}>
                  <span style={{ fontWeight: 600, fontSize: '0.95rem', color: '#2C3E50' }}>📋 Data Anak</span>
                  <div style={{ display: 'flex', gap: 6 }}>
                    {[['all','Semua'],['normal','Normal'],['risk','Berisiko']].map(([val, lbl]) => (
                      <button
                        key={val}
                        onClick={() => setFilter(val)}
                        style={{
                          padding: '5px 14px',
                          borderRadius: 20,
                          fontSize: '0.78rem',
                          fontWeight: 500,
                          border: '1.5px solid',
                          borderColor: filter === val ? '#1B5E20' : '#E0E4E8',
                          background: filter === val ? '#1B5E20' : 'white',
                          color: filter === val ? 'white' : '#7F8C8D',
                          cursor: 'pointer',
                          transition: 'all 0.15s',
                        }}
                      >
                        {lbl}
                      </button>
                    ))}
                  </div>
                </div>

                {loading ? (
                  <div style={{ textAlign: 'center', padding: '48px', color: '#999' }}>Memuat...</div>
                ) : (
                  <ChildTable
                    children={filtered}
                    onRowClick={c => { setEditChild(c); setShowForm(true) }}
                    onDelete={handleDelete}
                    onChartClick={c => navigate(`/child/${c.id}`)}
                  />
                )}
              </div>
            </>
          )}
        </div>
      </div>

      {/* Modals */}
      {showForm && (
        <ChildForm
          child={editChild}
          onSave={handleSave}
          onClose={() => { setShowForm(false); setEditChild(null) }}
        />
      )}
      {showSchedule && (
        <SchedulePanel onClose={() => setShowSchedule(false)} />
      )}
    </div>
  )
}
