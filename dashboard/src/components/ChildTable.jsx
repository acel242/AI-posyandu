import RiskBadge from './RiskBadge'

function calcAge(birthDate) {
  if (!birthDate) return '-'
  const birth = new Date(birthDate)
  const now = new Date()
  const months = (now.getFullYear() - birth.getFullYear()) * 12 + (now.getMonth() - birth.getMonth())
  if (months < 0) return ' baru'
  if (months < 12) return `${months} bln`
  const years = Math.floor(months / 12)
  const rem = months % 12
  return rem > 0 ? `${years} thn ${rem} bln` : `${years} thn`
}

export default function ChildTable({ children, onRowClick, onDelete, onChartClick }) {
  if (!children || children.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">👶</div>
        <div className="empty-state-text">Belum ada data anak</div>
        <div className="empty-state-sub">Tambahkan data anak pertama Anda</div>
      </div>
    )
  }

  return (
    <div className="table-wrap">
      <div style={{ overflowX: 'auto' }}>
        <table className="table">
          <thead>
            <tr>
              <th>Nama</th>
              <th>NIK</th>
              <th>JK</th>
              <th>Usia</th>
              <th>Status</th>
              <th>Aksi</th>
            </tr>
          </thead>
          <tbody>
            {children.map(child => (
              <tr key={child.id} onClick={() => onRowClick && onRowClick(child)}>
                <td className="child-name">{child.name}</td>
                <td className="child-nik">{child.nik || '-'}</td>
                <td>{child.gender === 'L' ? 'L' : 'P'}</td>
                <td>{calcAge(child.date_of_birth)}</td>
                <td><RiskBadge status={child.risk_status} /></td>
                <td onClick={e => e.stopPropagation()}>
                  <div style={{ display: 'flex', gap: 6, alignItems: 'center', flexWrap: 'nowrap' }}>
                    <button
                      className="btn btn-sm btn-secondary"
                      onClick={() => onRowClick && onRowClick(child)}
                    >Detail</button>
                    {onChartClick && (
                      <button
                        className="btn btn-sm btn-accent"
                        onClick={() => onChartClick(child)}
                        style={{ background: '#1565C0', color: '#fff' }}
                      >Chart</button>
                    )}
                    {onDelete && (
                      <button
                        className="btn btn-sm btn-danger"
                        onClick={() => onDelete(child.id)}
                      >Hapus</button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
