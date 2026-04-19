import { useState } from 'react'

const emptyForm = {
  name: '',
  nik: '',
  address: '',
  date_of_birth: '',
  gender: 'L',
  parent_name: '',
  parent_phone: '',
  parent_telegram_id: '',
  rt_rw: '001/001',
}

export default function ChildForm({ child, onSave, onClose }) {
  const isEdit = Boolean(child?.id)
  const [form, setForm] = useState(child ? {
    name: child.name || '',
    nik: child.nik || '',
    address: child.address || '',
    date_of_birth: child.date_of_birth || '',
    gender: child.gender || 'L',
    parent_name: child.parent_name || '',
    parent_phone: child.parent_phone || '',
    parent_telegram_id: child.parent_telegram_id || '',
    rt_rw: child.rt_rw || '001/001',
  } : emptyForm)
  const [saving, setSaving] = useState(false)

  const set = (field) => (e) => setForm(f => ({ ...f, [field]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.name.trim()) return alert('Nama anak harus diisi')
    if (!form.date_of_birth) return alert('Tanggal lahir harus diisi')
    setSaving(true)
    await onSave(form)
    setSaving(false)
  }

  return (
    <div className="modal-backdrop" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-header">
          <h2 className="modal-title">{isEdit ? '✏️ Edit Data Anak' : '➕ Tambah Data Anak'}</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <div className="form-group">
              <label className="form-label">Nama Anak *</label>
              <input className="form-input" value={form.name} onChange={set('name')} placeholder="Nama lengkap anak" required />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label className="form-label">NIK</label>
                <input className="form-input" value={form.nik} onChange={set('nik')} placeholder="16 digit NIK" />
              </div>
              <div className="form-group">
                <label className="form-label">Jenis Kelamin</label>
                <select className="form-select" value={form.gender} onChange={set('gender')}>
                  <option value="L">Laki-laki</option>
                  <option value="P">Perempuan</option>
                </select>
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Tanggal Lahir *</label>
              <input className="form-input" type="date" value={form.date_of_birth} onChange={set('date_of_birth')} required />
            </div>
            <div className="form-group">
              <label className="form-label">Alamat</label>
              <input className="form-input" value={form.address} onChange={set('address')} placeholder="Alamat lengkap" />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label className="form-label">Nama Orang Tua</label>
                <input className="form-input" value={form.parent_name} onChange={set('parent_name')} placeholder="Nama ayah/ibu" />
              </div>
              <div className="form-group">
                <label className="form-label">Telepon</label>
                <input className="form-input" value={form.parent_phone} onChange={set('parent_phone')} placeholder="08xxxxxxxxxx" />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label className="form-label">RT/RW</label>
                <input className="form-input" value={form.rt_rw} onChange={set('rt_rw')} placeholder="001/001" />
              </div>
              <div className="form-group">
                <label className="form-label">Telegram ID</label>
                <input className="form-input" value={form.parent_telegram_id} onChange={set('parent_telegram_id')} placeholder="Opsional" />
              </div>
            </div>
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>Batal</button>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? 'Menyimpan...' : 'Simpan'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
