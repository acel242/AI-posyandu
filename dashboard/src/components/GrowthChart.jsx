import { useState } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const WHO_WFA_BOY = [
  {mo:0,m:3.3},{mo:1,m:4.5},{mo:2,m:5.6},{mo:3,m:6.4},{mo:4,m:7.0},{mo:5,m:7.5},
  {mo:6,m:7.9},{mo:7,m:8.3},{mo:8,m:8.6},{mo:9,m:8.9},{mo:10,m:9.2},{mo:12,m:9.6},
  {mo:15,m:10.3},{mo:18,m:10.8},{mo:21,m:11.5},{mo:24,m:12.2},{mo:30,m:13.3},{mo:36,m:14.1},
  {mo:42,m:15.0},{mo:48,m:16.0},{mo:54,m:16.9},{mo:60,m:17.9}
]
const WHO_WFA_GIRL = [
  {mo:0,m:3.2},{mo:1,m:4.2},{mo:2,m:5.1},{mo:3,m:5.8},{mo:4,m:6.4},{mo:5,m:6.9},
  {mo:6,m:7.3},{mo:7,m:7.6},{mo:8,m:8.0},{mo:9,m:8.2},{mo:10,m:8.5},{mo:12,m:8.9},
  {mo:15,m:9.5},{mo:18,m:10.1},{mo:21,m:10.8},{mo:24,m:11.5},{mo:30,m:12.7},{mo:36,m:13.7},
  {mo:42,m:14.6},{mo:48,m:15.5},{mo:54,m:16.4},{mo:60,m:17.3}
]
const WHO_HFA_BOY = [
  {mo:0,m:49.9},{mo:3,m:61.4},{mo:6,m:67.6},{mo:9,m:72.1},{mo:12,m:75.7},{mo:18,m:82.3},
  {mo:24,m:87.8},{mo:30,m:92.9},{mo:36,m:97.7},{mo:42,m:102.3},{mo:48,m:106.8},{mo:54,m:111.2},{mo:60,m:115.5}
]
const WHO_HFA_GIRL = [
  {mo:0,m:49.1},{mo:3,m:60.2},{mo:6,m:66.2},{mo:9,m:70.6},{mo:12,m:74.1},{mo:18,m:80.7},
  {mo:24,m:86.4},{mo:30,m:91.5},{mo:36,m:96.1},{mo:42,m:100.5},{mo:48,m:104.9},{mo:54,m:109.1},{mo:60,m:113.2}
]

function getRef(chartType, gender) {
  if (chartType === 'wfa') return gender === 'L' ? WHO_WFA_BOY : WHO_WFA_GIRL
  return gender === 'L' ? WHO_HFA_BOY : WHO_HFA_GIRL
}

function getYLabel(chartType) {
  return chartType === 'wfa' ? 'Berat (kg)' : 'Tinggi (cm)'
}

function classify(z) {
  if (z === null || z === undefined) return 'unmeasured'
  if (z >= -1) return 'green'
  if (z >= -2) return 'yellow'
  return 'red'
}

function statusColor(s) {
  if (s === 'green') return '#4CAF50'
  if (s === 'yellow') return '#FFC107'
  if (s === 'red') return '#F44336'
  return '#9E9E9E'
}

export default function GrowthChart({ child, measurements, chartType = 'wfa' }) {
  const [activeChart, setActiveChart] = useState(chartType)

  if (!child || !measurements || measurements.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: 40, color: '#666', background: '#f8f8f8', borderRadius: 12 }}>
        <div style={{ fontSize: 48, marginBottom: 12 }}>&#128202;</div>
        <p>Belum ada data pengukuran untuk {child ? child.name : 'anak'} - growth chart akan muncul setelah data pertama diinput.</p>
      </div>
    )
  }

  const refData = getRef(activeChart, child.gender)
  const yLabel = getYLabel(activeChart)
  const valKey = activeChart === 'wfa' ? 'weight_kg' : 'height_cm'

  const chartData = measurements
    .filter(m => m.age_months != null && m[valKey] != null)
    .map(m => ({
      age_months: m.age_months,
      child_val: m[valKey],
      z_wfa: m.z_score_wfa,
      z_hfa: m.z_score_hfa,
      overall: m.overall_status,
      date: m.date,
    }))

  const yMin = activeChart === 'wfa' ? 3 : 50
  const yMax = activeChart === 'wfa' ? 25 : 125
  const latest = chartData.length > 0 ? chartData[chartData.length - 1] : null
  const latestZ = activeChart === 'wfa' ? latest?.z_wfa : latest?.z_hfa

  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload || !payload.length) return null
    const d = payload[0]?.payload
    if (!d) return null
    return (
      <div style={{ background: '#fff', border: '1px solid #ddd', borderRadius: 8, padding: 10, fontSize: 12 }}>
        <p style={{ margin: 0, fontWeight: 700 }}>Umur: {d.age_months} bulan</p>
        <p style={{ margin: '4px 0 0' }}>Tanggal: {d.date || '-'}</p>
        <p style={{ margin: '4px 0 0' }}>Nilai: <strong style={{ color: '#1565C0' }}>{d.child_val}</strong></p>
        {activeChart === 'wfa' && d.z_wfa != null && (
          <p style={{ margin: '4px 0 0' }}>Z BB/U: <strong style={{ color: statusColor(classify(d.z_wfa)) }}>{d.z_wfa}</strong></p>
        )}
        {activeChart === 'hfa' && d.z_hfa != null && (
          <p style={{ margin: '4px 0 0' }}>Z TB/U: <strong style={{ color: statusColor(classify(d.z_hfa)) }}>{d.z_hfa}</strong></p>
        )}
      </div>
    )
  }

  return (
    <div style={{ background: '#fff', borderRadius: 16, padding: 20, boxShadow: '0 2px 12px rgba(0,0,0,0.08)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div>
          <h3 style={{ margin: 0, color: '#1B5E20', fontSize: 16 }}>&#128202; Growth Chart - {child.name}</h3>
          <p style={{ margin: '4px 0 0', color: '#666', fontSize: 12 }}>
            {child.gender === 'L' ? 'Laki-laki' : 'Perempuan'} | {child.date_of_birth}
          </p>
        </div>
        <div style={{ display: 'flex', gap: 6 }}>
          <button
            onClick={() => setActiveChart('wfa')}
            style={{
              padding: '6px 14px',
              borderRadius: 20,
              border: 'none',
              cursor: 'pointer',
              fontWeight: activeChart === 'wfa' ? 700 : 400,
              background: activeChart === 'wfa' ? '#1B5E20' : '#e8f5e9',
              color: activeChart === 'wfa' ? '#fff' : '#1B5E20',
              fontSize: 12,
            }}
          >
            Berat/Umur
          </button>
          <button
            onClick={() => setActiveChart('hfa')}
            style={{
              padding: '6px 14px',
              borderRadius: 20,
              border: 'none',
              cursor: 'pointer',
              fontWeight: activeChart === 'hfa' ? 700 : 400,
              background: activeChart === 'hfa' ? '#1B5E20' : '#e8f5e9',
              color: activeChart === 'hfa' ? '#fff' : '#1B5E20',
              fontSize: 12,
            }}
          >
            Tinggi/Umur
          </button>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
          <XAxis
            dataKey="age_months"
            label={{ value: 'Umur (bulan)', position: 'insideBottom', offset: -2, fontSize: 11 }}
            tick={{ fontSize: 11 }}
            ticks={[0, 6, 12, 18, 24, 30, 36, 42, 48, 54, 60]}
          />
          <YAxis
            label={{ value: yLabel, angle: -90, position: 'insideLeft', fontSize: 11 }}
            domain={[yMin, yMax]}
            tick={{ fontSize: 11 }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Line
            type="monotone"
            data={refData}
            dataKey="m"
            name="Median WHO"
            stroke="#4CAF50"
            strokeWidth={1.5}
            strokeDasharray="5 3"
            dot={false}
          />
          <Line
            type="monotone"
            data={chartData}
            dataKey="child_val"
            name={activeChart === 'wfa' ? 'Berat (kg)' : 'Tinggi (cm)'}
            stroke="#1565C0"
            strokeWidth={2.5}
            dot={{ fill: '#1565C0', r: 5, strokeWidth: 2, stroke: '#fff' }}
            activeDot={{ r: 7, fill: '#1565C0' }}
          />
        </LineChart>
      </ResponsiveContainer>

      <div style={{ display: 'flex', gap: 16, marginTop: 12, fontSize: 11, flexWrap: 'wrap', color: '#666' }}>
        <span><span style={{ color: '#4CAF50' }}>- - -</span> Median WHO</span>
        <span><span style={{ color: '#1565C0' }}>-</span> {child.name}</span>
        <span style={{ color: '#4CAF50' }}>&#9679;</span> Normal
        <span style={{ color: '#FFC107' }}>&#9679;</span> Risiko
        <span style={{ color: '#F44336' }}>&#9679;</span> Buruk
      </div>

      {latest && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, marginTop: 16 }}>
          <div style={{ background: '#f8f8f8', borderRadius: 10, padding: '10px 12px', textAlign: 'center' }}>
            <p style={{ margin: 0, fontSize: 10, color: '#888', textTransform: 'uppercase' }}>Terakhir Diukur</p>
            <p style={{ margin: '4px 0 0', fontSize: 16, fontWeight: 700 }}>{latest.date || '-'}</p>
          </div>
          <div style={{ background: '#f8f8f8', borderRadius: 10, padding: '10px 12px', textAlign: 'center' }}>
            <p style={{ margin: 0, fontSize: 10, color: '#888', textTransform: 'uppercase' }}>
              {activeChart === 'wfa' ? 'Z-score BB/U' : 'Z-score TB/U'}
            </p>
            <p style={{ margin: '4px 0 0', fontSize: 16, fontWeight: 700, color: statusColor(classify(latestZ)) }}>
              {latestZ != null ? latestZ.toFixed(2) : '-'}
            </p>
          </div>
          <div style={{ background: '#f8f8f8', borderRadius: 10, padding: '10px 12px', textAlign: 'center' }}>
            <p style={{ margin: 0, fontSize: 10, color: '#888', textTransform: 'uppercase' }}>Status</p>
            <p style={{ margin: '4px 0 0', fontSize: 16, fontWeight: 700, color: statusColor(latest.overall) }}>
              {latest.overall === 'green' ? 'Normal' : latest.overall === 'yellow' ? 'Risiko' : latest.overall === 'red' ? 'Buruk' : '-'}
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
