import { useState, useEffect } from 'react'

export default function SchedulePanel({ isOpen, onClose }) {
  const [schedules, setSchedules] = useState([])
  const [loading, setLoading] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ title: '', description: '', scheduled_date: '', scheduled_time: '08:00', reminder_days_before: 1, target_role: 'warga' })
  const [submitting, setSubmitting] = useState(false)
  const [msg, setMsg] = useState(null)

  useEffect(() => {
    if (!isOpen) return
    loadSchedules()
  }, [isOpen])

  const loadSchedules = async () => {
    setLoading(true)
    try {
      const r = await fetch('/api/schedules')
      const data = await r.json()
      setSchedules(Array.isArray(data) ? data : [])
    } catch { setSchedules([]) }
    setLoading(false)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.title || !form.scheduled_date) return
    setSubmitting(true)
    setMsg(null)
    try {
      const r = await fetch('/api/schedules', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })
      const result = await r.json()
      if (result.id || r.ok) {
        setMsg({ ok: true, text: '✅ Jadwal berhasil disimpan' })
        setForm({ title: '', description: '', scheduled_date: '', scheduled_time: '08:00', reminder_days_before: 1, target_role: 'warga' })
        setShowForm(false)
        loadSchedules()
      } else {
        setMsg({ ok: false, text: result.error || 'Gagal menyimpan' })
      }
    } catch {
      setMsg({ ok: false, text: 'Koneksi gagal' })
    }
    setSubmitting(false)
  }

  const handleDelete = async (id) => {
    if (!confirm('Hapus jadwal ini?')) return
    try {
      await fetch(`/api/schedules/${id}`, { method: 'DELETE' })
      loadSchedules()
    } catch { }
  }

  const panelStyle = {
    position: 'fixed', top: 0, right: 0, bottom: 0, width: 420, maxWidth: '100vw',
    background: '#fff', boxShadow: '-4px 0 24px rgba(0,0,0,0.12)', zIndex: 200,
    display: 'flex', flexDirection: 'column', transition: 'transform 0.3s ease',
    transform: isOpen ? 'translateX(0)' : 'translateX(100%)',
  }

  const overlayStyle = {
    position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.3)', zIndex: 199,
    opacity: isOpen ? 1 : 0, pointerEvents: isOpen ? 'auto' : 'none',
    transition: 'opacity 0.3s',
  }

  const formatDate = (d) => {
    if (!d) return '—'
    const [y, mo, day] = d.split('-')
    return `${day}/${mo}/${y}`
  }

  return (
    <>
      <div style={overlayStyle} onClick={onClose} />
      <div style={panelStyle}>
        {/* Header */}
        <div style={{ padding: '16px 20px', borderBottom: '1px solid #eee', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#f8fafc' }}>
          <div>
            <h2 style={{ margin: 0, fontSize: 16, color: '#1a3a2a' }}>📅 Kelola Jadwal Posyandu</h2>
            <p style={{ margin: '2px 0 0', fontSize: 12, color: '#666' }}>Atur jadwal & pengingat otomatis</p>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', fontSize: 20, cursor: 'pointer', color: '#666' }}>✕</button>
        </div>

        {/* Body */}
        <div style={{ flex: 1, overflowY: 'auto', padding: 16 }}>
          {/* Add button */}
          {!showForm && (
            <button onClick={() => setShowForm(true)} style={{ width: '100%', background: '#16a34a', color: 'white', border: 'none', borderRadius: 8, padding: '10px 0', fontSize: 14, cursor: 'pointer', marginBottom: 12 }}>
              + Tambah Jadwal Baru
            </button>
          )}

          {/* Form */}
          {showForm && (
            <div style={{ background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: 10, padding: 14, marginBottom: 12 }}>
              <h3 style={{ margin: '0 0 10px', fontSize: 14, color: '#166534' }}>Jadwal Baru</h3>
              <form onSubmit={handleSubmit}>
                <label style={{ fontSize: 12, display: 'block', marginBottom: 8 }}>
                  Nama Kegiatan <span style={{ color: 'red' }}>*</span>
                  <input value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} placeholder="Posyandu Bulanan" required style={{ width: '100%', marginTop: 4, padding: '6px 8px', borderRadius: 6, border: '1px solid #ccc', fontSize: 13, boxSizing: 'border-box' }} />
                </label>
                <label style={{ fontSize: 12, display: 'block', marginBottom: 8 }}>
                  Lokasi
                  <input value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} placeholder="Balai Desa Patakbanteng" style={{ width: '100%', marginTop: 4, padding: '6px 8px', borderRadius: 6, border: '1px solid #ccc', fontSize: 13, boxSizing: 'border-box' }} />
                </label>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginBottom: 8 }}>
                  <label style={{ fontSize: 12 }}>
                    Tanggal <span style={{ color: 'red' }}>*</span>
                    <input type="date" value={form.scheduled_date} onChange={e => setForm(f => ({ ...f, scheduled_date: e.target.value }))} required style={{ width: '100%', marginTop: 4, padding: '6px 8px', borderRadius: 6, border: '1px solid #ccc', fontSize: 13 }} />
                  </label>
                  <label style={{ fontSize: 12 }}>
                    Waktu
                    <input type="time" value={form.scheduled_time} onChange={e => setForm(f => ({ ...f, scheduled_time: e.target.value }))} style={{ width: '100%', marginTop: 4, padding: '6px 8px', borderRadius: 6, border: '1px solid #ccc', fontSize: 13 }} />
                  </label>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginBottom: 8 }}>
                  <label style={{ fontSize: 12 }}>
                    Reminder H-n
                    <select value={form.reminder_days_before} onChange={e => setForm(f => ({ ...f, reminder_days_before: parseInt(e.target.value) }))} style={{ width: '100%', marginTop: 4, padding: '6px 8px', borderRadius: 6, border: '1px solid #ccc', fontSize: 13 }}>
                      {[1, 2, 3, 7].map(n => <option key={n} value={n}>H-{n}</option>)}
                    </select>
                  </label>
                  <label style={{ fontSize: 12 }}>
                    Target
                    <select value={form.target_role} onChange={e => setForm(f => ({ ...f, target_role: e.target.value }))} style={{ width: '100%', marginTop: 4, padding: '6px 8px', borderRadius: 6, border: '1px solid #ccc', fontSize: 13 }}>
                      <option value="warga">Warga (Orang Tua)</option>
                      <option value="kader">Kader</option>
                      <option value="bidan">Bidan</option>
                      <option value="all">Semua</option>
                    </select>
                  </label>
                </div>
                {msg && (
                  <div style={{ padding: '6px 10px', borderRadius: 6, marginBottom: 8, fontSize: 12, background: msg.ok ? '#dcfce7' : '#fef2f2', color: msg.ok ? '#166534' : '#991b1b' }}>
                    {msg.text}
                  </div>
                )}
                <div style={{ display: 'flex', gap: 8 }}>
                  <button type="submit" disabled={submitting} style={{ flex: 1, background: '#16a34a', color: 'white', border: 'none', borderRadius: 6, padding: '8px 0', fontSize: 13, cursor: submitting ? 'not-allowed' : 'pointer', opacity: submitting ? 0.6 : 1 }}>
                    {submitting ? 'Menyimpan...' : '💾 Simpan'}
                  </button>
                  <button type="button" onClick={() => { setShowForm(false); setMsg(null) }} style={{ flex: 1, background: '#e5e7eb', color: '#333', border: 'none', borderRadius: 6, padding: '8px 0', fontSize: 13, cursor: 'pointer' }}>
                    Batal
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* List */}
          {loading ? (
            <div style={{ textAlign: 'center', color: '#999', padding: 20, fontSize: 13 }}>Memuat...</div>
          ) : schedules.length === 0 ? (
            <div style={{ textAlign: 'center', color: '#999', padding: 20, fontSize: 13 }}>Belum ada jadwal. Tambahkan jadwal pertama.</div>
          ) : (
            schedules.map(s => (
              <div key={s.id} style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 10, padding: '12px 14px', marginBottom: 10 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 'bold', fontSize: 14, color: '#334155' }}>{s.title}</div>
                    {s.description && <div style={{ fontSize: 12, color: '#666', marginTop: 2 }}>{s.description}</div>}
                    <div style={{ fontSize: 12, color: '#888', marginTop: 4 }}>
                      📅 {formatDate(s.scheduled_date)} · 🕗 {s.scheduled_time || '08:00'} WIB
                    </div>
                    <div style={{ display: 'flex', gap: 6, marginTop: 6, flexWrap: 'wrap' }}>
                      <span style={{ background: '#dbeafe', color: '#1e40af', padding: '2px 8px', borderRadius: 12, fontSize: 11 }}>
                        H-{s.reminder_days_before || 1}
                      </span>
                      <span style={{ background: '#f3e8ff', color: '#6b21a8', padding: '2px 8px', borderRadius: 12, fontSize: 11 }}>
                        {s.target_role === 'all' ? 'Semua' : s.target_role?.charAt(0).toUpperCase() + s.target_role?.slice(1)}
                      </span>
                    </div>
                  </div>
                  <button onClick={() => handleDelete(s.id)} style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer', fontSize: 16, padding: '4px 6px' }}>🗑</button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </>
  )
}
