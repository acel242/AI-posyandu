import { useState, useEffect } from 'react'
import Navbar from '../components/Navbar'
import RiskBadge from '../components/RiskBadge'
import AlertBadge from '../components/AlertBadge'
import AlertPanel from '../components/AlertPanel'
import ChildTable from '../components/ChildTable'
import ChildForm from '../components/ChildForm'

function formatDateIndonesian() {
  const opts = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }
  return new Date().toLocaleDateString('id-ID', opts)
}

export default function BidanDashboard({ user, onLogout, onBellClick }) {
  const [children, setChildren] = useState([])
  const [stats, setStats] = useState({ total: 0, green: 0, yellow: 0, red: 0, unmeasured: 0 })
  const [loading, setLoading] = useState(true)
  const [alerts, setAlerts] = useState([])
  const [alertStats, setAlertStats] = useState({ sent: 0, failed: 0, pending: 0 })
  const [panelOpen, setPanelOpen] = useState(false)
  const [alertLoading, setAlertLoading] = useState(false)
  const [selectedChild, setSelectedChild] = useState(null)
  const [formData, setFormData] = useState({ weight_kg: '', height_cm: '', age_months: '', notes: '' })
  const [submitting, setSubmitting] = useState(false)
  const [submitMsg, setSubmitMsg] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [editChild, setEditChild] = useState(null)
  const [filter, setFilter] = useState('all')

  const loadData = () => {
    setLoading(true)
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
  }

  useEffect(() => { loadData() }, [])

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

  const handleSubmitMeasurement = async (e) => {
    e.preventDefault()
    if (!formData.weight_kg || !formData.height_cm) return
    setSubmitting(true)
    setSubmitMsg(null)
    try {
      const child = selectedChild
      const payload = {
        weight_kg: parseFloat(formData.weight_kg),
        height_cm: parseFloat(formData.height_cm),
        measured_by: user.username,
        notes: formData.notes,
      }
      const res = await fetch(`/api/children/${child.id}/health-record`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      const result = await res.json()
      if (result.success) {
        const { status, category, z_score } = result.classification
        setSubmitMsg({ ok: true, text: `${child.name}: ${category} (z=${z_score})` })
        setSelectedChild(null)
        setFormData({ weight_kg: '', height_cm: '', age_months: '', notes: '' })
        loadData()
      } else {
        setSubmitMsg({ ok: false, text: result.error || 'Gagal menyimpan' })
      }
    } catch (_) {
      setSubmitMsg({ ok: false, text: 'Koneksi gagal' })
    }
    setSubmitting(false)
  }

  const unmeasuredCases = children.filter(c => c.risk_status === 'unmeasured')
  const redCases = children.filter(c => c.risk_status === 'red')
  const yellowCases = children.filter(c => c.risk_status === 'yellow')

  const filteredChildren = children.filter(c => {
    if (filter === 'normal') return c.risk_status === 'green'
    if (filter === 'risk') return c.risk_status === 'red' || c.risk_status === 'yellow'
    return true
  })

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

          {/* Unmeasured warning */}
          {unmeasuredCases.length > 0 && (
            <div className="warning-card">
              <span className="icon">⚠️</span>
              <span><strong>{unmeasuredCases.length} anak</strong> belum ditimbang lebih dari 30 hari</span>
            </div>
          )}

          {/* Stats */}
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon total">👶</div>
              <div><div className="stat-label">Total Anak</div><div className="stat-value">{stats.total || 0}</div></div>
            </div>
            <div className="stat-card">
              <div className="stat-icon normal">🟢</div>
              <div><div className="stat-label">Normal</div><div className="stat-value">{stats.green || 0}</div></div>
            </div>
            <div className="stat-card">
              <div className="stat-icon" style={{background:'#FEF3C7'}}>🟡</div>
              <div><div className="stat-label">Risiko</div><div className="stat-value">{yellowCases.length}</div></div>
            </div>
            <div className="stat-card">
              <div className="stat-icon risk">🔴</div>
              <div><div className="stat-label">Rujuk</div><div className="stat-value">{redCases.length}</div></div>
            </div>
          </div>

          {/* Measurement Form */}
          {selectedChild && (
            <div className="card" style={{ marginBottom: 16, borderLeft: '4px solid #27AE60', background: '#F0FDF4' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                <h3 style={{ margin: 0, fontSize: '1rem', color: '#166534' }}>📏 Input Pengukuran — {selectedChild.name}</h3>
                <button onClick={() => setSelectedChild(null)} style={{ background: 'none', border: 'none', fontSize: 18, cursor: 'pointer', color: '#666' }}>✕</button>
              </div>
              <p style={{ margin: '0 0 12px', fontSize: '0.85rem', color: '#666' }}>{selectedChild.parent_name} · {selectedChild.address}</p>
              <form onSubmit={handleSubmitMeasurement}>
                <div className="form-row">
                  <div className="form-group">
                    <label className="form-label">Berat (kg) *</label>
                    <input className="form-input" type="number" step="0.1" min="0" required value={formData.weight_kg}
                      onChange={e => setFormData(f => ({ ...f, weight_kg: e.target.value }))} placeholder="0.0" />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Tinggi (cm) *</label>
                    <input className="form-input" type="number" step="0.1" min="0" required value={formData.height_cm}
                      onChange={e => setFormData(f => ({ ...f, height_cm: e.target.value }))} placeholder="0.0" />
                  </div>
                </div>
                <div className="form-group">
                  <label className="form-label">Catatan</label>
                  <input className="form-input" value={formData.notes}
                    onChange={e => setFormData(f => ({ ...f, notes: e.target.value }))} placeholder="Opsional" />
                </div>
                {submitMsg && (
                  <div style={{ padding: '8px 12px', borderRadius: 6, marginBottom: 10, fontSize: '0.85rem',
                    background: submitMsg.ok ? '#dcfce7' : '#fef2f2', color: submitMsg.ok ? '#166534' : '#991b1b' }}>
                    {submitMsg.ok ? '✅ ' : '❌ '}{submitMsg.text}
                  </div>
                )}
                <div style={{ display: 'flex', gap: 8 }}>
                  <button type="submit" className="btn btn-primary btn-sm" disabled={submitting}>
                    {submitting ? 'Menyimpan...' : '💾 Simpan & Klasifikasi'}
                  </button>
                  <button type="button" className="btn btn-secondary btn-sm" onClick={() => setSelectedChild(null)}>Batal</button>
                </div>
              </form>
            </div>
          )}

          {/* Red cases */}
          {redCases.length > 0 && (
            <div style={{ marginBottom: 20 }}>
              <div className="section-header">
                <span className="section-title">🔴 Kasus Rujuk Segera ({redCases.length})</span>
              </div>
              {redCases.map(c => (
                <div key={c.id} className="card" style={{ marginBottom: 8, borderLeft: '4px solid #E74C3C', background: '#FEF2F2' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 8 }}>
                    <div>
                      <div style={{ fontWeight: 600, marginBottom: 2 }}>{c.name}</div>
                      <div style={{ fontSize: '0.8rem', color: '#666' }}>{c.parent_name} · {c.address}</div>
                      <div style={{ fontSize: '0.75rem', color: '#888', fontFamily: 'monospace' }}>NIK: {c.nik}</div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <RiskBadge status="red" />
                      <button className="btn btn-primary btn-sm" onClick={() => setSelectedChild(c)}>📏 Ukur</button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Yellow cases */}
          {yellowCases.length > 0 && (
            <div style={{ marginBottom: 20 }}>
              <div className="section-header">
                <span className="section-title">🟡 Kasus Kunjungan Rumah ({yellowCases.length})</span>
              </div>
              {yellowCases.map(c => (
                <div key={c.id} className="card" style={{ marginBottom: 8, borderLeft: '4px solid #F39C12', background: '#FEFCE8' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 8 }}>
                    <div>
                      <div style={{ fontWeight: 600, marginBottom: 2 }}>{c.name}</div>
                      <div style={{ fontSize: '0.8rem', color: '#666' }}>{c.parent_name} · {c.address}</div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <RiskBadge status="yellow" />
                      <button className="btn btn-secondary btn-sm" onClick={() => setSelectedChild(c)}>📏 Ukur</button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Child Table */}
          <div className="section-header">
            <span className="section-title">📋 Data Anak</span>
            <div className="filter-bar">
              <button className={`filter-chip ${filter === 'all' ? 'active' : ''}`} onClick={() => setFilter('all')}>Semua</button>
              <button className={`filter-chip ${filter === 'normal' ? 'active' : ''}`} onClick={() => setFilter('normal')}>Normal</button>
              <button className={`filter-chip ${filter === 'risk' ? 'active' : ''}`} onClick={() => setFilter('risk')}>Berisiko</button>
            </div>
          </div>

          {loading ? (
            <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>Memuat...</div>
          ) : (
            <ChildTable
              children={filteredChildren}
              onRowClick={(child) => { setSelectedChild(child) }}
              onDelete={null}
            />
          )}
        </div>
      </div>

      {/* FAB */}
      <button className="fab" onClick={() => { setEditChild(null); setShowForm(true) }}>+</button>

      {/* Child Form Modal */}
      {showForm && (
        <ChildForm
          child={editChild}
          onSave={async (formData) => {
            const res = await fetch('/api/children', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(formData),
            })
            const data = await res.json()
            if (data.success || data.id) { setShowForm(false); loadData() }
            else alert('Gagal: ' + (data.error || 'Unknown'))
          }}
          onClose={() => { setShowForm(false); setEditChild(null) }}
        />
      )}

      {/* Alert Panel */}
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
