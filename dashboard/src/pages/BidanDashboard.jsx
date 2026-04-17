import { useState, useEffect } from 'react'
import RiskBadge from '../components/RiskBadge'

export default function BidanDashboard({ user, onLogout }) {
  const [children, setChildren] = useState([])
  const [stats, setStats] = useState({ total: 0, green: 0, yellow: 0, red: 0, unmeasured: 0 })
  const [loading, setLoading] = useState(true)
  const [selectedChild, setSelectedChild] = useState(null)
  const [formData, setFormData] = useState({ weight_kg: '', height_cm: '', age_months: '', vitamin_a: false, notes: '' })
  const [submitting, setSubmitting] = useState(false)
  const [submitMsg, setSubmitMsg] = useState(null)

  const loadData = () => {
    setLoading(true)
    fetch('/api/children')
      .then(r => r.json())
      .then(data => { setChildren(data); setLoading(false) })
      .catch(() => setLoading(false))
    fetch('/api/stats')
      .then(r => r.json())
      .then(setStats)
      .catch(() => {})
  }

  useEffect(() => { loadData() }, [])

  const unmeasuredCases = children.filter(c => c.risk_status === 'unmeasured')
  const redCases = children.filter(c => c.risk_status === 'red')
  const yellowCases = children.filter(c => c.risk_status === 'yellow')

  const cardStyle = (bg) => ({
    padding: '14px 12px', borderRadius: 12, background: bg, color: 'white',
    textAlign: 'center', flex: '1 1 100px', fontSize: 13,
  })

  const caseCardStyle = {
    background: '#fff', borderRadius: 12, padding: '12px 14px',
    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
    flexWrap: 'wrap', gap: 8, marginBottom: 10,
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!formData.weight_kg || !formData.height_cm || !formData.age_months) return
    setSubmitting(true)
    setSubmitMsg(null)
    try {
      const child = selectedChild
      const payload = {
        weight_kg: parseFloat(formData.weight_kg),
        height_cm: parseFloat(formData.height_cm),
        age_months: parseInt(formData.age_months),
        gender: child.gender,
        vitamin_a: formData.vitamin_a,
        notes: formData.notes,
        recorded_by: user.id,
      }
      const res = await fetch(`/api/children/${child.id}/health-record`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      const result = await res.json()
      if (result.success) {
        const { status, label } = result.classification
        setSubmitMsg({ ok: true, text: `${child.name}: ${label} (z=${result.classification.z_score?.toFixed(2)})` })
        setSelectedChild(null)
        setFormData({ weight_kg: '', height_cm: '', age_months: '', vitamin_a: false, notes: '' })
        loadData()
      } else {
        setSubmitMsg({ ok: false, text: result.error || 'Gagal menyimpan' })
      }
    } catch (err) {
      setSubmitMsg({ ok: false, text: 'Koneksi gagal' })
    }
    setSubmitting(false)
  }

  return (
    <div style={{ padding: '1rem', fontFamily: 'system-ui, sans-serif', maxWidth: 1000, margin: '0 auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 8, marginBottom: 20 }}>
        <div>
          <h1 style={{ margin: 0, color: '#1a3a2a', fontSize: 20 }}>Dashboard Bidan</h1>
          <p style={{ margin: '4px 0 0', color: '#666', fontSize: 13 }}>
            Posyandu Patakbanteng — {user.username}
          </p>
        </div>
        <button onClick={onLogout} style={{ background: 'none', border: 'none', color: '#666', cursor: 'pointer', fontSize: 14, padding: 0 }}>Keluar</button>
      </div>

      {/* Alert Cards */}
      <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginBottom: 20 }}>
        <div style={cardStyle('#94a3b8')}>
          <div style={{ fontSize: 28, fontWeight: 'bold' }}>{unmeasuredCases.length}</div>
          <div style={{ fontSize: 12 }}>⚪ Belum Diukur</div>
        </div>
        <div style={cardStyle('#22c55e')}>
          <div style={{ fontSize: 28, fontWeight: 'bold' }}>{stats.green}</div>
          <div style={{ fontSize: 12 }}>🟢 Normal</div>
        </div>
        <div style={cardStyle('#eab308')}>
          <div style={{ fontSize: 28, fontWeight: 'bold' }}>{yellowCases.length}</div>
          <div style={{ fontSize: 12 }}>🟡 Risiko</div>
        </div>
        <div style={cardStyle('#ef4444')}>
          <div style={{ fontSize: 28, fontWeight: 'bold' }}>{redCases.length}</div>
          <div style={{ fontSize: 12 }}>🔴 Rujuk</div>
        </div>
        <div style={{ ...cardStyle('#3b82f6'), flex: '1 1 120px' }}>
          <div style={{ fontSize: 28, fontWeight: 'bold' }}>{stats.total}</div>
          <div style={{ fontSize: 12 }}>Total Anak</div>
        </div>
      </div>

      {/* Measurement Form */}
      {selectedChild && (
        <div style={{ background: '#f0fdf4', border: '2px solid #22c55e', borderRadius: 12, padding: 16, marginBottom: 20 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <h3 style={{ margin: 0, color: '#166534', fontSize: 15 }}>
              📏 Input Pengukuran — {selectedChild.name}
            </h3>
            <button onClick={() => { setSelectedChild(null); setSubmitMsg(null) }}
              style={{ background: 'none', border: 'none', color: '#666', cursor: 'pointer', fontSize: 18 }}>✕</button>
          </div>
          <p style={{ margin: '0 0 12px', fontSize: 13, color: '#666' }}>
            {selectedChild.parent_name} · {selectedChild.address}
          </p>
          <form onSubmit={handleSubmit}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 10, marginBottom: 10 }}>
              <label style={{ fontSize: 13 }}>
                Berat (kg) <span style={{ color: 'red' }}>*</span>
                <input type="number" step="0.1" min="0" required value={formData.weight_kg}
                  onChange={e => setFormData(f => ({ ...f, weight_kg: e.target.value }))}
                  style={{ width: '100%', marginTop: 4, padding: '6px 8px', borderRadius: 6, border: '1px solid #ccc', fontSize: 13, boxSizing: 'border-box' }} />
              </label>
              <label style={{ fontSize: 13 }}>
                Tinggi (cm) <span style={{ color: 'red' }}>*</span>
                <input type="number" step="0.1" min="0" required value={formData.height_cm}
                  onChange={e => setFormData(f => ({ ...f, height_cm: e.target.value }))}
                  style={{ width: '100%', marginTop: 4, padding: '6px 8px', borderRadius: 6, border: '1px solid #ccc', fontSize: 13, boxSizing: 'border-box' }} />
              </label>
              <label style={{ fontSize: 13 }}>
                Umur (bulan) <span style={{ color: 'red' }}>*</span>
                <input type="number" min="0" required value={formData.age_months}
                  onChange={e => setFormData(f => ({ ...f, age_months: e.target.value }))}
                  style={{ width: '100%', marginTop: 4, padding: '6px 8px', borderRadius: 6, border: '1px solid #ccc', fontSize: 13, boxSizing: 'border-box' }} />
              </label>
            </div>
            <div style={{ display: 'flex', gap: 10, alignItems: 'center', marginBottom: 10 }}>
              <label style={{ fontSize: 13, display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                <input type="checkbox" checked={formData.vitamin_a}
                  onChange={e => setFormData(f => ({ ...f, vitamin_a: e.target.checked }))} />
                Vitamin A
              </label>
            </div>
            <label style={{ fontSize: 13, display: 'block', marginBottom: 10 }}>
              Catatan
              <textarea value={formData.notes} rows={2}
                onChange={e => setFormData(f => ({ ...f, notes: e.target.value }))}
                style={{ width: '100%', marginTop: 4, padding: '6px 8px', borderRadius: 6, border: '1px solid #ccc', fontSize: 13, boxSizing: 'border-box', resize: 'vertical' }} />
            </label>
            {submitMsg && (
              <div style={{ padding: '8px 12px', borderRadius: 6, marginBottom: 8, fontSize: 13,
                background: submitMsg.ok ? '#dcfce7' : '#fef2f2',
                color: submitMsg.ok ? '#166534' : '#991b1b' }}>
                {submitMsg.ok ? '✅ ' : '❌ '}{submitMsg.text}
              </div>
            )}
            <button type="submit" disabled={submitting}
              style={{ background: '#16a34a', color: 'white', border: 'none', borderRadius: 8, padding: '8px 20px', fontSize: 13, cursor: submitting ? 'not-allowed' : 'pointer', opacity: submitting ? 0.6 : 1 }}>
              {submitting ? 'Menyimpan...' : '💾 Simpan & Klasifikasi'}
            </button>
          </form>
        </div>
      )}

      {/* Unmeasured Cases — call to action */}
      {unmeasuredCases.length > 0 && !selectedChild && (
        <div style={{ marginBottom: 20 }}>
          <h3 style={{ color: '#64748b', marginBottom: 10, fontSize: 15 }}>
            ⚪ Belum Diukur ({unmeasuredCases.length})
          </h3>
          {unmeasuredCases.map(c => (
            <div key={c.id} style={{ ...caseCardStyle, background: '#f8fafc', border: '1px solid #e2e8f0' }}>
              <div>
                <div style={{ fontWeight: 'bold', color: '#334155', fontSize: 14 }}>{c.name}</div>
                <div style={{ fontSize: 12, color: '#666' }}>{c.parent_name} · {c.address}</div>
                <div style={{ fontSize: 12, color: '#888' }}>NIK: {c.nik}</div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <RiskBadge status="unmeasured" />
                <button onClick={() => setSelectedChild(c)}
                  style={{ background: '#16a34a', color: 'white', border: 'none', borderRadius: 6, padding: '6px 14px', fontSize: 12, cursor: 'pointer' }}>
                  📏 Ukur
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Red Cases */}
      <div style={{ marginBottom: 20 }}>
        <h3 style={{ color: '#ef4444', marginBottom: 10, fontSize: 15 }}>🔴 Kasus Rujuk Segera ({redCases.length})</h3>
        {loading ? (
          <div style={{ color: '#999', padding: 12 }}>Memuat...</div>
        ) : redCases.length === 0 ? (
          <div style={{ background: 'white', padding: 24, borderRadius: 12, textAlign: 'center', color: '#999', fontSize: 14 }}>Tidak ada kasus rojo</div>
        ) : (
          redCases.map(c => (
            <div key={c.id} style={{ ...caseCardStyle, background: '#fef2f2', border: '1px solid #fecaca' }}>
              <div>
                <div style={{ fontWeight: 'bold', color: '#991b1b', fontSize: 14 }}>{c.name}</div>
                <div style={{ fontSize: 12, color: '#666' }}>{c.parent_name} · {c.address}</div>
                <div style={{ fontSize: 12, color: '#888' }}>NIK: {c.nik}</div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <RiskBadge status="red" />
                <div style={{ marginTop: 6, fontSize: 12, color: '#666' }}>{c.last_posyandu_date || '—'}</div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Yellow Cases */}
      <div>
        <h3 style={{ color: '#ca8a04', marginBottom: 10, fontSize: 15 }}>🟡 Kasus Kunjungan Rumah ({yellowCases.length})</h3>
        {yellowCases.length === 0 ? (
          <div style={{ background: 'white', padding: 24, borderRadius: 12, textAlign: 'center', color: '#999', fontSize: 14 }}>Tidak ada kasus kuning</div>
        ) : (
          yellowCases.map(c => (
            <div key={c.id} style={{ ...caseCardStyle, background: '#fefce8', border: '1px solid #fde047' }}>
              <div>
                <div style={{ fontWeight: 'bold', color: '#854d0e', fontSize: 14 }}>{c.name}</div>
                <div style={{ fontSize: 12, color: '#666' }}>{c.parent_name} · {c.address}</div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <RiskBadge status="yellow" />
                <div style={{ marginTop: 6, fontSize: 12, color: '#666' }}>{c.last_posyandu_date || '—'}</div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
