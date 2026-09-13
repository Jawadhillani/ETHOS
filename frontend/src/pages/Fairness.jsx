import { useState, useEffect } from 'react'
import { getFairnessReport } from '../api'

const COLORS = ['#00d4ff','#f59e0b','#10b981','#a78bfa','#f43f5e','#34d399','#f472b6','#fbbf24','#60a5fa']

const RACE_COLORS = {
  'Black':           '#f59e0b',
  'White':           '#00e5ff',
  'East Asian':      '#a78bfa',
  'Indian':          '#34d399',
  'Latino_Hispanic': '#10b981',
  'Middle Eastern':  '#fbbf24',
  'Southeast Asian': '#f472b6',
}

// Gaussian PDF — for score distribution visualisation
function gauss(x, mu, sigma) {
  return Math.exp(-0.5 * ((x - mu) / sigma) ** 2) / (sigma * Math.sqrt(2 * Math.PI))
}

function ScoreDistChart({ perGroup, threshold }) {
  if (!perGroup) return null

  const W = 640, H = 260
  const pad = { top: 20, right: 28, bottom: 52, left: 52 }
  const iW = W - pad.left - pad.right
  const iH = H - pad.top - pad.bottom

  const X_MIN = -0.10, X_MAX = 0.42
  const N = 220

  // Build curves
  const groups = Object.entries(perGroup).map(([name, m]) => ({
    name,
    mu:    m.score_mean,
    sigma: m.score_std,
    far:   m.far_at_threshold,
    color: RACE_COLORS[name] ?? '#8aafd4',
  }))

  // Find max density for y-scale
  let yMax = 0
  groups.forEach(({ mu, sigma }) => {
    const peak = gauss(mu, mu, sigma)
    if (peak > yMax) yMax = peak
  })
  yMax *= 1.12

  const xS = x => pad.left + ((x - X_MIN) / (X_MAX - X_MIN)) * iW
  const yS = y => pad.top + iH - (y / yMax) * iH

  // Build SVG path points for each group
  const xs = Array.from({ length: N }, (_, i) => X_MIN + (i / (N - 1)) * (X_MAX - X_MIN))

  const yTicks = [0, 2, 4, 6]
  const xTickVals = [-0.1, 0, 0.1, 0.2, 0.3, 0.4]
  const threshX = xS(threshold ?? 0.181)

  return (
    <div>
      <div style={{ padding: '14px 20px', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
        <div style={{ fontSize: 10, fontWeight: 800, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: 4 }}>
          Impostor Score Distributions by Race
        </div>
        <div style={{ fontSize: 10, color: 'rgba(120,155,190,0.5)' }}>
          Gaussian approximation from group statistics · vertical line = decision threshold τ
        </div>
      </div>

      {/* Legend */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px 14px', padding: '10px 20px', borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
        {groups.sort((a,b) => b.far - a.far).map(g => (
          <div key={g.name} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ width: 20, height: 3, borderRadius: 2, background: g.color, display: 'inline-block', boxShadow: `0 0 4px ${g.color}` }}/>
            <span style={{ fontSize: 9.5, color: 'rgba(170,200,240,0.7)', fontFamily: 'Inter,sans-serif' }}>
              {g.name.replace('_',' ')}
            </span>
            <span style={{ fontSize: 9, color: g.color, fontWeight: 700, opacity: 0.8 }}>
              {(g.far * 100).toFixed(3)}%
            </span>
          </div>
        ))}
      </div>

      <div style={{ padding: '8px 0 0' }}>
        <svg width="100%" viewBox={`0 0 ${W} ${H}`} style={{ display: 'block', overflow: 'visible' }}>

          {/* Grid lines */}
          {yTicks.map(v => (
            <g key={v}>
              <line x1={pad.left} x2={pad.left + iW} y1={yS(v)} y2={yS(v)}
                stroke="rgba(255,255,255,0.04)" strokeWidth={1}/>
              <text x={pad.left - 7} y={yS(v) + 4} textAnchor="end"
                fill="rgba(125,159,194,0.5)" fontSize={9} fontFamily="Inter,sans-serif">{v}</text>
            </g>
          ))}
          {xTickVals.map(v => (
            <g key={v}>
              <text x={xS(v)} y={pad.top + iH + 14} textAnchor="middle"
                fill="rgba(125,159,194,0.5)" fontSize={9} fontFamily="Inter,sans-serif">
                {v.toFixed(1)}
              </text>
            </g>
          ))}

          {/* Axis labels */}
          <text x={pad.left + iW / 2} y={H - 4} textAnchor="middle"
            fill="rgba(125,159,194,0.45)" fontSize={10} fontFamily="Inter,sans-serif">
            ArcFace Cosine Similarity Score
          </text>
          <text x={12} y={pad.top + iH / 2} textAnchor="middle"
            fill="rgba(125,159,194,0.45)" fontSize={10} fontFamily="Inter,sans-serif"
            transform={`rotate(-90,12,${pad.top + iH / 2})`}>
            Density
          </text>

          {/* FAR shaded regions (area right of threshold per group) */}
          {groups.map(({ name, mu, sigma, color }) => {
            const farPoints = xs.filter(x => x >= (threshold ?? 0.181))
            if (!farPoints.length) return null
            const pts = [
              `${xS(threshold ?? 0.181)},${yS(0)}`,
              ...farPoints.map(x => `${xS(x)},${yS(gauss(x, mu, sigma))}`),
              `${xS(X_MAX)},${yS(0)}`,
            ].join(' ')
            return <polygon key={`far-${name}`} points={pts} fill={color} opacity={0.06}/>
          })}

          {/* Distribution curves */}
          {groups.map(({ name, mu, sigma, color }) => {
            const pts = xs.map(x => `${xS(x)},${yS(gauss(x, mu, sigma))}`).join(' ')
            return (
              <polyline key={name} points={pts} fill="none"
                stroke={color} strokeWidth={2} strokeLinejoin="round" opacity={0.85}/>
            )
          })}

          {/* Decision threshold line */}
          <line x1={threshX} x2={threshX} y1={pad.top} y2={pad.top + iH}
            stroke="rgba(255,255,255,0.45)" strokeWidth={1.5} strokeDasharray="5,3"/>
          <text x={threshX + 5} y={pad.top + 13}
            fill="rgba(255,255,255,0.55)" fontSize={9} fontWeight={700} fontFamily="Inter,sans-serif">
            τ = {(threshold ?? 0.181).toFixed(3)}
          </text>
          <text x={threshX + 5} y={pad.top + 24}
            fill="rgba(255,100,100,0.55)" fontSize={8.5} fontFamily="Inter,sans-serif">
            FAR zone →
          </text>
        </svg>
      </div>
    </div>
  )
}

function FarBarChart({ data, label }) {
  if (!data) return null
  const groups = Object.keys(data)
  const fars = groups.map(g => data[g].far_at_threshold * 100)
  const indices = [...fars.keys()].sort((a, b) => fars[a] - fars[b])
  const sortedGroups = indices.map(i => groups[i])
  const sortedFars = indices.map(i => fars[i])
  const maxFar = Math.max(...sortedFars) * 1.2 || 1

  const barH = 26
  const gap = 12
  const labelW = 140
  const chartW = 360
  const valW = 72
  const totalH = sortedGroups.length * (barH + gap)

  return (
    <svg width="100%" viewBox={`0 0 ${labelW + chartW + valW} ${totalH}`} style={{ display: 'block', overflow: 'visible' }}>
      {sortedGroups.map((group, idx) => {
        const barWidth = (sortedFars[idx] / maxFar) * chartW
        const y = idx * (barH + gap)
        const color = COLORS[idx % COLORS.length]
        return (
          <g key={group}>
            <text x={labelW - 10} y={y + barH / 2 + 4}
              textAnchor="end" fill="rgba(125,159,194,0.85)" fontSize={11}
              fontFamily="Inter,sans-serif">{group}</text>
            <rect x={labelW} y={y} width={chartW} height={barH} rx={5} fill="rgba(255,255,255,0.03)" />
            <rect x={labelW} y={y} width={Math.max(barWidth, 3)} height={barH} rx={5}
              fill={color} opacity={0.8} />
            <rect x={labelW} y={y} width={Math.max(barWidth, 3)} height={barH} rx={5}
              fill={`url(#shine-${idx})`} opacity={0.3} />
            <defs>
              <linearGradient id={`shine-${idx}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="white" stopOpacity={0.3} />
                <stop offset="100%" stopColor="white" stopOpacity={0} />
              </linearGradient>
            </defs>
            <text x={labelW + chartW + 8} y={y + barH / 2 + 4}
              fill="rgba(240,244,255,0.75)" fontSize={10} fontWeight={700}
              fontFamily="Inter,sans-serif">
              {sortedFars[idx].toFixed(3)}%
            </text>
          </g>
        )
      })}
    </svg>
  )
}

function ArcGauge({ fmrd, threshold = 1.5 }) {
  const [mounted, setMounted] = useState(false)
  useEffect(() => { const t = setTimeout(() => setMounted(true), 80); return () => clearTimeout(t) }, [])

  const pass = fmrd <= threshold
  const color = pass ? '#10b981' : '#f43f5e'
  const glow = pass ? 'rgba(16,185,129,0.65)' : 'rgba(244,63,94,0.65)'

  const R = 54, cx = 70, cy = 70
  const startAngle = 210
  const totalArc = 300

  const pct = Math.min(fmrd / (threshold * 2.5), 1)
  const fillDeg = pct * totalArc

  function polarToXY(angle, r) {
    const rad = (angle - 90) * Math.PI / 180
    return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) }
  }

  function arcPath(startDeg, endDeg, r) {
    const s = polarToXY(startDeg, r)
    const e = polarToXY(endDeg, r)
    const large = endDeg - startDeg > 180 ? 1 : 0
    return `M ${s.x} ${s.y} A ${r} ${r} 0 ${large} 1 ${e.x} ${e.y}`
  }

  const tRatio = threshold / (threshold * 2.5)
  // Animate arc using pathLength normalization
  const animFillDeg = mounted ? fillDeg : 0

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12, padding: '24px 16px' }}>
      <div style={{ fontSize: 9.5, fontWeight: 800, letterSpacing: '0.14em', textTransform: 'uppercase', color: 'var(--text-muted)' }}>
        FMRD Score
      </div>

      <div style={{ position: 'relative', width: 140, height: 100 }}>
        <svg width={140} height={100} viewBox="0 0 140 100">
          {/* Background arc */}
          <path d={arcPath(startAngle, startAngle + totalArc, R)} fill="none"
            stroke="rgba(255,255,255,0.06)" strokeWidth={10} strokeLinecap="round" />
          {/* Filled arc — animated */}
          {fillDeg > 0 && (
            <path
              d={arcPath(startAngle, startAngle + animFillDeg, R)}
              fill="none"
              stroke={color}
              strokeWidth={10}
              strokeLinecap="round"
              style={{
                filter: `drop-shadow(0 0 10px ${glow})`,
                transition: 'all 1.4s cubic-bezier(0.4,0,0.2,1) 0.2s',
              }}
            />
          )}
          {/* Threshold marker */}
          <path d={arcPath(startAngle + tRatio * totalArc - 1, startAngle + tRatio * totalArc + 1, R + 6)}
            fill="none" stroke="rgba(255,255,255,0.55)" strokeWidth={2} />
          {/* Center value */}
          <text x={cx} y={cy + 4} textAnchor="middle"
            fill={color} fontSize={22} fontWeight={900}
            fontFamily="'Orbitron',Inter,sans-serif"
            style={{ filter: `drop-shadow(0 0 16px ${glow})` }}>
            {fmrd >= 10 ? fmrd.toFixed(1) : fmrd.toFixed(2)}
          </text>
          <text x={cx + 18} y={cy + 16} textAnchor="middle"
            fill={color} fontSize={10} fontWeight={700}>×</text>
        </svg>
      </div>

      <span className={`tag ${pass ? 'tag-pass' : 'tag-fail'}`}
        style={!pass ? { animation: 'glow-pulse 2s ease-in-out infinite' } : {}}>
        {pass ? `✓ ≤ ${threshold}× · PASS` : `✗ > ${threshold}× · FAIL`}
      </span>
    </div>
  )
}

function ComplianceRow({ label, a }) {
  const r = a.fairness_ratios
  const c = a.compliance
  const s = a.summary
  const pass = c.fmrd_compliant
  return (
    <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
      <td style={{ padding: '14px 20px', fontWeight: 700, color: 'var(--text-pri)', fontSize: 14 }}>
        {label}
      </td>
      <td style={{ padding: '14px 20px', textAlign: 'center' }}>
        <span style={{
          fontSize: 18, fontWeight: 900, fontFamily: "'Orbitron',sans-serif",
          color: pass ? 'var(--success)' : 'var(--danger)',
          textShadow: pass ? '0 0 14px rgba(16,185,129,0.6)' : '0 0 14px rgba(244,63,94,0.6)',
        }}>
          {r.fmrd.toFixed(2)}<span style={{ fontSize: 12 }}>×</span>
        </span>
      </td>
      <td style={{ padding: '14px 20px', textAlign: 'center', color: 'var(--text-sec)', fontSize: 13 }}>
        {r.disparate_impact.toFixed(4)}
      </td>
      <td style={{ padding: '14px 20px', textAlign: 'center' }}>
        <span className={pass ? 'tag tag-pass' : 'tag tag-fail'}>
          {pass ? '✓ PASS' : '✗ FAIL'}
        </span>
      </td>
      <td style={{ padding: '14px 20px', color: 'var(--text-muted)', fontSize: 12 }}>
        {s.best_far_group} → {s.worst_far_group}
      </td>
    </tr>
  )
}

const AXES = [['race','Race'], ['gender','Gender'], ['age','Age']]

const AXIS_ACCENTS = { race: '#f43f5e', gender: '#00e5ff', age: '#f59e0b' }
const AXIS_ICONS   = { race: '◈', gender: '⟺', age: '◉' }

function SectionDivider({ label }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 16 }}>
      <div style={{ height: 1, width: 24, background: 'linear-gradient(to right, transparent, rgba(0,229,255,0.4))' }} />
      <span style={{ fontSize: 10, fontWeight: 800, letterSpacing: '0.15em', textTransform: 'uppercase', color: 'var(--accent)' }}>
        {label}
      </span>
      <div style={{ flex: 1, height: 1, background: 'rgba(0,229,255,0.07)' }} />
    </div>
  )
}

export default function Fairness() {
  const [report, setReport]   = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState('')

  async function load() {
    setLoading(true); setError('')
    try { setReport(await getFairnessReport()) }
    catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  const audits    = report?.audits
  const threshold = report?.metadata?.threshold

  return (
    <div style={{ maxWidth: 1140, margin: '0 auto', padding: '48px 28px 60px' }}>

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', marginBottom: 40 }}>
        <div>
          <div className="page-eyebrow">
            <span style={{
              display: 'inline-block', width: 5, height: 5, borderRadius: '50%',
              background: 'var(--accent)', animation: 'dot-pulse 2s ease-in-out infinite',
            }} />
            FairFace 86k · τ = {threshold ?? '0.1810'}
          </div>
          <h2 style={{
            fontSize: 40, fontWeight: 900, letterSpacing: '-0.03em',
            background: 'linear-gradient(135deg, var(--text-pri) 0%, var(--accent) 100%)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text',
            marginBottom: 8,
          }}>Fairness Audit</h2>
          <p className="section-sub" style={{ fontSize: 16 }}>
            Per-demographic False Acceptance Rates · FMRD · Disparate Impact
          </p>
        </div>
        <button className={report ? 'btn-ghost' : 'btn-primary'} onClick={load} disabled={loading}>
          {loading
            ? <><span className="spin" style={{ marginRight: 8 }}>◌</span>Loading…</>
            : report ? '↻ Refresh' : '◈  Load Dashboard'
          }
        </button>
      </div>

      {error && (
        <div style={{
          color: 'var(--danger)', marginBottom: 20,
          background: 'rgba(244,63,94,0.06)', border: '1px solid rgba(244,63,94,0.22)',
          borderRadius: 10, padding: '12px 16px', fontSize: 13,
        }}>{error}</div>
      )}

      {/* Empty state */}
      {!audits && !loading && (
        <div style={{
          textAlign: 'center', padding: '90px 20px',
          border: '1px dashed rgba(0,229,255,0.12)', borderRadius: 20,
          color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 20,
          background: 'rgba(0,229,255,0.015)',
          animation: 'border-pulse 4s ease-in-out infinite',
        }}>
          <div style={{
            width: 88, height: 88, borderRadius: '50%',
            border: '1px solid rgba(0,229,255,0.2)',
            background: 'rgba(0,229,255,0.04)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 38, color: 'rgba(0,229,255,0.35)',
            boxShadow: '0 0 40px rgba(0,229,255,0.06)',
            animation: 'float 5s ease-in-out infinite',
          }}>⚖</div>
          <div>
            <div style={{ fontSize: 16, fontWeight: 600, color: 'var(--text-sec)', marginBottom: 6 }}>
              No fairness data loaded
            </div>
            <div style={{ fontSize: 13 }}>Click "Load Dashboard" to pull audit data</div>
          </div>
        </div>
      )}

      {/* ── Summary trio ── */}
      {audits && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 16, marginBottom: 32 }}>
            {AXES.map(([key, label], idx) => {
              const a = audits[key]
              const pass = a.compliance.fmrd_compliant
              const fmrd = a.fairness_ratios.fmrd
              const accent = AXIS_ACCENTS[key]
              const icon = AXIS_ICONS[key]
              return (
                <div key={key} style={{
                  background: `radial-gradient(ellipse at top left, ${pass ? 'rgba(16,185,129,0.09)' : `${accent}12`} 0%, rgba(14,22,46,0.98) 65%)`,
                  border: `1px solid ${pass ? 'rgba(16,185,129,0.22)' : `${accent}35`}`,
                  borderTop: `2px solid ${pass ? '#10b981' : accent}`,
                  borderRadius: 18,
                  padding: '26px 22px',
                  display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10,
                  position: 'relative', overflow: 'hidden',
                  boxShadow: `0 8px 40px ${pass ? 'rgba(16,185,129,0.06)' : `${accent}14`}`,
                  animation: `card-in 0.55s cubic-bezier(0.34,1.56,0.64,1) ${idx * 0.12}s both${!pass ? `, danger-pulse 3.5s ease-in-out ${1 + idx * 0.3}s infinite` : ''}`,
                  transition: 'transform 0.25s ease, box-shadow 0.25s ease',
                  cursor: 'default',
                }}
                onMouseEnter={e => {
                  e.currentTarget.style.transform = 'translateY(-6px) scale(1.02)'
                  e.currentTarget.style.boxShadow = `0 24px 56px ${pass ? 'rgba(16,185,129,0.14)' : `${accent}28`}`
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.transform = ''
                  e.currentTarget.style.boxShadow = `0 8px 40px ${pass ? 'rgba(16,185,129,0.06)' : `${accent}14`}`
                }}>
                  {/* Top glow */}
                  <div style={{
                    position: 'absolute', top: 0, left: 0, right: 0, height: 1,
                    background: `linear-gradient(90deg, transparent, ${pass ? '#10b981' : accent}70, transparent)`,
                  }} />
                  {/* Radial bg glow on fail */}
                  {!pass && (
                    <div style={{
                      position: 'absolute', top: -30, left: '50%', transform: 'translateX(-50%)',
                      width: 160, height: 160, borderRadius: '50%',
                      background: `radial-gradient(circle, ${accent}10 0%, transparent 70%)`,
                      pointerEvents: 'none',
                    }} />
                  )}

                  <div style={{ fontSize: 22, color: pass ? '#10b981' : accent, opacity: 0.6 }}>{icon}</div>
                  <div style={{
                    fontSize: 9, fontWeight: 800, letterSpacing: '0.18em',
                    textTransform: 'uppercase', color: 'var(--text-muted)',
                  }}>{label} FMRD</div>
                  <div style={{
                    fontSize: 54, fontWeight: 900, fontFamily: "'Orbitron','Inter',sans-serif",
                    letterSpacing: '-0.02em', lineHeight: 1,
                    color: pass ? '#10b981' : accent,
                    textShadow: `0 0 36px ${pass ? 'rgba(16,185,129,0.5)' : `${accent}66`}`,
                  }}>
                    {fmrd >= 10 ? fmrd.toFixed(1) : fmrd.toFixed(2)}
                    <span style={{ fontSize: 22 }}>×</span>
                  </div>
                  <span className={`tag ${pass ? 'tag-pass' : 'tag-fail'}`} style={{
                    marginTop: 4,
                    animation: !pass ? 'glow-pulse 2s ease-in-out infinite' : undefined,
                  }}>
                    {pass ? '✓ PASS' : '✗ FAIL'}
                  </span>
                </div>
              )
            })}
          </div>

          {/* Compliance table */}
          <SectionDivider label="Compliance Summary" />
          <div style={{
            background: 'linear-gradient(145deg, rgba(22,34,62,0.96), rgba(14,22,46,0.98))',
            border: '1px solid rgba(255,255,255,0.07)',
            borderRadius: 16, overflow: 'hidden', marginBottom: 40,
          }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.07)' }}>
                  {['Axis', 'FMRD', 'Disp. Impact', 'Verdict', 'FAR Range (best → worst)'].map(h => (
                    <th key={h} style={{
                      padding: '12px 20px', fontSize: 9.5, fontWeight: 800,
                      letterSpacing: '0.1em', textTransform: 'uppercase', color: 'var(--text-muted)',
                      textAlign: h === 'Axis' || h.includes('Range') ? 'left' : 'center',
                      background: 'rgba(0,0,0,0.2)',
                    }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {AXES.map(([key, label]) => (
                  <ComplianceRow key={key} label={label} a={audits[key]} />
                ))}
              </tbody>
            </table>
          </div>

          {/* ── Score distribution chart — Race ── */}
          <SectionDivider label="Impostor Score Distributions · Race" />
          <div style={{
            background: 'linear-gradient(145deg, rgba(20,30,56,0.96), rgba(14,22,46,0.98))',
            border: '1px solid rgba(255,255,255,0.07)',
            borderRadius: 16, overflow: 'hidden', marginBottom: 32,
          }}>
            <ScoreDistChart
              perGroup={audits.race.per_group}
              threshold={threshold}
            />
          </div>

          {/* Per-axis breakdown */}
          {AXES.map(([key, label]) => (
            <div key={key} style={{ marginBottom: 36 }}>
              <SectionDivider label={`${label} Breakdown`} />
              <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 16 }}>
                <div style={{
                  background: 'linear-gradient(145deg, rgba(20,30,56,0.96), rgba(14,22,46,0.98))',
                  border: '1px solid rgba(255,255,255,0.07)',
                  borderRadius: 14, padding: '22px 24px',
                }}>
                  <div style={{
                    fontSize: 10, fontWeight: 700, letterSpacing: '0.12em',
                    textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: 20,
                  }}>
                    False Acceptance Rate by {label}
                  </div>
                  <FarBarChart data={audits[key].per_group} label={label} />
                </div>

                <div style={{
                  background: 'linear-gradient(145deg, rgba(20,30,56,0.96), rgba(14,22,46,0.98))',
                  border: '1px solid rgba(255,255,255,0.07)',
                  borderRadius: 14,
                }}>
                  <ArcGauge fmrd={audits[key].fairness_ratios.fmrd} />
                </div>
              </div>
            </div>
          ))}
        </>
      )}
    </div>
  )
}
