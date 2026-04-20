import { useState, useEffect } from 'react'
import Sidebar from '../components/Sidebar'
import RiskBadge from '../components/RiskBadge'
import AlertPanel from '../components/AlertPanel'
import ChildTable from '../components/ChildTable'
import ChildForm from '../components/ChildForm'

function StatBox({ icon, label, value, color = '#1B5E20' }) {
  return (
    <div style={{
      background: 'white',
      borderRadius: 16,
      padding: '18px 22px',
      display: 'flex',
      alignItems: 'center',
      gap: 14,
      boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
      flex: 1,
      minWidth: 140,
    }}>
      <div style={{
        width: 48, height: 48,
        borderRadius: 12,
        background: color + '18',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: '1.3rem',
        flexShrink: 0,
      }}>
        {icon}
      </div>
      <div>
        <div style={{ fontSize: '0.72rem', color: '#7F8C8D', marginBottom: 2, fontWeight: 500 }}>{label}</div>
        <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#2C3E50', lineHeight: 1 }}>{value}</div>
      </div>
    </div>
  )
}

export default function BidanDashboard({ user, onLogout }) {
  const [children, setChildren] = useState([])
  const [stats, setStats] = useState({ total: 0, green: 0, yellow: 0, red: 0, unmeasured: 0 })
  const [loading, setLoading] = useState(true)
  const [alerts, setAlerts] = useState([])
  const [alertStats, setAlertStats] = useState({ sent: 0, failed: 0, pending: 0 })
  const [panelOpen, setPanelOpen] = useState(false)
  const [alertLoading, setAlertLoading] = useState(false)
  const [selectedChild, setSelectedChild] = useState(null)
  const [formData, setFormData] = useState({ weight_kg: '', height_cm: '', notes: '' })
  const [submitting, setSubmitting] = useState(false)
  const [submitMsg, setSubmitMsg] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [editChild, setEditChild] = useState(null)
  const [filter, setFilter] = useState('all')
  const [activeNav, setActiveNav] = useState('/')

  useEffect(() => { loadData() }, [])

  function loadData() {
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
      if (result.success || result.id) {
        const { status, category, z_score } = result.classification || {}
        setSubmitMsg({ ok: true, text: `${child.name}: ${category || status} (z=${z_score || 'n/a'})` })
        setSelectedChild(null)
        setFormData({ weight_kg: '', height_cm: '', notes: '' })
        loadData()
      } else {
        setSubmitMsg({ ok: false, text: result.error || 'Gagal menyimpan' })
      }
    } catch (_) {
      setSubmitMsg({ ok: false, text: 'Koneksi gagal' })
    }
    setSubmitting(false)
  }

  const redCases = children.filter(c => c.risk_status === 'red')
  const yellowCases = children.filter(c => c.risk_status === 'yellow')
  const filteredChildren = children.filter(c => {
    if (filter === 'normal') return c.risk_status === 'green'
    if (filter === 'risk') return c.risk_status === 'red' || c.risk_status === 'yellow'
    return true
  })

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#F5F6FA' }}>
      <Sidebar
        user={user}
        activePath={activeNav}
        onNavigate={p => setActiveNav(p)}
        onLogout={onLogout}
        alertFailedCount={alertStats.failed || 0}
      />

      <div style={{ flex: 1, marginLeft: 240 }}>
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
            <h1 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#2C3E50' }}>🏥 Dashboard Bidan</h1>
            <p style={{ fontSize: '0.75rem', color: '#7F8C8D' }}>
              {new Date().toLocaleDateString('id-ID', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
            </p>
          </div>
          <button onClick={() => setShowForm(true)} style={{
            display: 'flex', alignItems: 'center', gap: 6,
            padding: '8px 18px', borderRadius: 10, border: 'none',
            background: '#1B5E20', fontSize: '0.85rem', fontWeight: 600,
            cursor: 'pointer', color: 'white',
          }}>+ Tambah Anak</button>
        </div>

        {/* Content */}
        <div style={{ padding: '24px 28px' }}>
          {/* Welcome */}
          <div style={{
            background: 'linear-gradient(135deg, #1B5E20 0%, #2E7D32 60%, #388E3C 100%)',
            borderRadius: 20, padding: '22px 28px', color: 'white', marginBottom: 20,
          }}>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: 4 }}>
              Selamat Datang, {user?.username || 'Bidan'} 👋
            </h2>
            <p style={{ opacity: 0.85, fontSize: '0.875rem' }}>
              {stats.total > 0
                ? `${stats.total} anak terdaftar · ${redCases.length} rujuk · ${yellowCases.length} risiko`
                : 'Belum ada data anak'}
            </p>
          </div>

          {/* Measurement Form */}
          {selectedChild && (
            <div style={{
              background: 'white', borderRadius: 16, padding: 20, marginBottom: 20,
              borderLeft: '4px solid #27AE60',
              boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                <h3 style={{ margin: 0, fontSize: '1rem', color: '#166534' }}>
                  📏 Input Pengukuran — {selectedChild.name}
                </h3>
                <button onClick={() => setSelectedChild(null)} style={{ background: 'none', border: 'none', fontSize: 18, cursor: 'pointer', color: '#666' }}>✕</button>
              </div>
              <p style={{ margin: '0 0 12px', fontSize: '0.85rem', color: '#666' }}>
                {selectedChild.parent_name} · {selectedChild.address}
              </p>
              <form onSubmit={handleSubmitMeasurement}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 12 }}>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 500, marginBottom: 4 }}>Berat (kg) *</label>
                    <input style={{ width: '100%', padding: '9px 12px', border: '1.5px solid #E0E4E8', borderRadius: 8, fontSize: '0.9rem' }}
                      type="number" step="0.1" min="0" required value={formData.weight_kg}
                      onChange={e => setFormData(f => ({ ...f, weight_kg: e.target.value }))} placeholder="0.0" />
                  </div>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 500, marginBottom: 4 }}>Tinggi (cm) *</label>
                    <input style={{ width: '100%', padding: '9px 12px', border: '1.5px solid #E0E4E8', borderRadius: 8, fontSize: '0.9rem' }}
                      type="number" step="0.1" min="0" required value={formData.height_cm}
                      onChange={e => setFormData(f => ({ ...f, height_cm: e.target.value }))} placeholder="0.0" />
                  </div>
                </div>
                <div style={{ marginBottom: 12 }}>
                  <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 500, marginBottom: 4 }}>Catatan</label>
                  <input style={{ width: '100%', padding: '9px 12px', border: '1.5px solid #E0E4E8', borderRadius: 8, fontSize: '0.9rem' }}
                    value={formData.notes} onChange={e => setFormData(f => ({ ...f, notes: e.target.value }))} placeholder="Opsional" />
                </div>
                {submitMsg && (
                  <div style={{ padding: '8px 12px', borderRadius: 6, marginBottom: 10, fontSize: '0.85rem',
                    background: submitMsg.ok ? '#dcfce7' : '#fef2f2', color: submitMsg.ok ? '#166534' : '#991b1b' }}>
                    {submitMsg.ok ? '✅ ' : '❌ '}{submitMsg.text}
                  </div>
                )}
                <div style={{ display: 'flex', gap: 8 }}>
                  <button type="submit" disabled={submitting} style={{
                    padding: '8px 18px', borderRadius: 8, border: 'none',
                    background: '#1B5E20', color: 'white', fontSize: '0.875rem', fontWeight: 500, cursor: 'pointer',
                  }}>
                    {submitting ? 'Menyimpan...' : '💾 Simpan & Klasifikasi'}
                  </button>
                  <button type="button" onClick={() => setSelectedChild(null)} style={{
                    padding: '8px 18px', borderRadius: 8, border: '1.5px solid #E0E4E8',
                    background: 'white', color: '#666', fontSize: '0.875rem', cursor: 'pointer',
                  }}>Batal</button>
                </div>
              </form>
            </div>
          )}

          {/* Stats */}
          <div style={{ display: 'flex', gap: 12, marginBottom: 24, flexWrap: 'wrap' }}>
            <StatBox icon="👶" label="Total Anak" value={stats.total || 0} color="#1B5E20" />
            <StatBox icon="✅" label="Normal" value={stats.green || 0} color="#2E7D32" />
            <StatBox icon="🟡" label="Risiko" value={yellowCases.length} color="#F57C00" />
            <StatBox icon="🔴" label="Rujuk" value={redCases.length} color="#C62828" />
          </div>

          {/* Red cases */}
          {redCases.length > 0 && (
            <div style={{ marginBottom: 24 }}>
              <div style={{ fontWeight: 600, fontSize: '0.95rem', color: '#2C3E50', marginBottom: 10 }}>🔴 Kasus Rujuk Segera ({redCases.length})</div>
              {redCases.map(c => (
                <div key={c.id} style={{
                  background: 'white', borderRadius: 12, padding: '14px 16px', marginBottom: 8,
                  borderLeft: '4px solid #E74C3C', boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 8,
                }}>
                  <div>
                    <div style={{ fontWeight: 600, marginBottom: 2 }}>{c.name}</div>
                    <div style={{ fontSize: '0.8rem', color: '#666' }}>{c.parent_name} · {c.address}</div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <RiskBadge status="red" />
                    <button onClick={() => setSelectedChild(c)} style={{
                      padding: '6px 14px', borderRadius: 8, border: 'none',
                      background: '#1B5E20', color: 'white', fontSize: '0.8rem', fontWeight: 500, cursor: 'pointer',
                    }}>📏 Ukur</button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Yellow cases */}
          {yellowCases.length > 0 && (
            <div style={{ marginBottom: 24 }}>
              <div style={{ fontWeight: 600, fontSize: '0.95rem', color: '#2C3E50', marginBottom: 10 }}>🟡 Kasus Kunjungan Rumah ({yellowCases.length})</div>
              {yellowCases.map(c => (
                <div key={c.id} style={{
                  background: 'white', borderRadius: 12, padding: '14px 16px', marginBottom: 8,
                  borderLeft: '4px solid #F39C12', boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 8,
                }}>
                  <div>
                    <div style={{ fontWeight: 600, marginBottom: 2 }}>{c.name}</div>
                    <div style={{ fontSize: '0.8rem', color: '#666' }}>{c.parent_name} · {c.address}</div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <RiskBadge status="yellow" />
                    <button onClick={() => setSelectedChild(c)} style={{
                      padding: '6px 14px', borderRadius: 8, border: '1.5px solid #E0E4E8',
                      background: 'white', color: '#666', fontSize: '0.8rem', fontWeight: 500, cursor: 'pointer',
                    }}>📏 Ukur</button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Child Table */}
          <div style={{ background: 'white', borderRadius: 16, overflow: 'hidden', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
            <div style={{ padding: '16px 20px', borderBottom: '1px solid #F0F0F0', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontWeight: 600, fontSize: '0.95rem', color: '#2C3E50' }}>📋 Data Anak</span>
              <div style={{ display: 'flex', gap: 6 }}>
                {[['all','Semua'],['normal','Normal'],['risk','Berisiko']].map(([val, lbl]) => (
                  <button key={val} onClick={() => setFilter(val)} style={{
                    padding: '5px 14px', borderRadius: 20, fontSize: '0.78rem', fontWeight: 500,
                    border: '1.5px solid ' + (filter === val ? '#1B5E20' : '#E0E4E8'),
                    background: filter === val ? '#1B5E20' : 'white',
                    color: filter === val ? 'white' : '#7F8C8D', cursor: 'pointer',
                  }}>{lbl}</button>
                ))}
              </div>
            </div>
            {loading ? (
              <div style={{ textAlign: 'center', padding: 48, color: '#999' }}>Memuat...</div>
            ) : (
              <ChildTable
                children={filteredChildren}
                onRowClick={c => setSelectedChild(c)}
                onDelete={null}
              />
            )}
          </div>
        </div>
      </div>

      {/* FAB */}
      <button onClick={() => { setEditChild(null); setShowForm(true) }} style={{
        position: 'fixed', bottom: 28, right: 28, width: 54, height: 54,
        borderRadius: '50%', background: '#1B5E20', color: 'white', fontSize: '1.5rem',
        border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.2)', cursor: 'pointer', zIndex: 50,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>+</button>

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

      {panelOpen && (
        <AlertPanel
          isOpen={panelOpen}
          onClose={() => setPanelOpen(false)}
          alerts={alerts}
          stats={alertStats}
          onRetry={handleRetry}
          loading={alertLoading}
        />
      )}
    </div>
  )
}
