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

export default function ChildTable({ children, onRowClick, onDelete }) {
  if (children.length === 0) {
    return (
      <div className="table-wrap" style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
        Belum ada data anak
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
              <tr key={child.id} onClick={() => onRowClick(child)}>
                <td style={{ fontWeight: 500 }}>{child.name}</td>
                <td style={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>{child.nik}</td>
                <td>{child.gender === 'L' ? 'L' : 'P'}</td>
                <td>{calcAge(child.date_of_birth)}</td>
                <td><RiskBadge status={child.risk_status} /></td>
                <td onClick={e => e.stopPropagation()}>
                  <button
                    className="btn btn-sm btn-secondary"
                    onClick={() => onRowClick(child)}
                    style={{ marginRight: 6 }}
                  >Edit</button>
                  {onDelete && (
                    <button
                      className="btn btn-sm btn-danger"
                      onClick={() => onDelete(child.id)}
                    >Hapus</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
