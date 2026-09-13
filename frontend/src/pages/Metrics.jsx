import { useState } from 'react'
import { getMetrics } from '../api'

const COLORS = ['#00d4ff', '#f59e0b', '#10b981', '#a78bfa', '#f43f5e']

function CmcChart({ rankK, nProbes, nGallery }) {
  const W = 620, H = 300
  const pad = { top: 24, right: 32, bottom: 52, left: 58 }
  const iW = W - pad.left - pad.right
  const iH = H - pad.top - pad.bottom
  const n  = rankK.length

  const xS = i => pad.left + (i / (n - 1)) * iW
  const yS = v => pad.top + iH - v * iH

  const linePoints = rankK.map((v, i) => `${xS(i)},${yS(v)}`).join(' ')
  const areaPoints = [
    `${pad.left},${pad.top + iH}`,
    ...rankK.map((v, i) => `${xS(i)},${yS(v)}`),
    `${pad.left + iW},${pad.top + iH}`,
  ].join(' ')

  const yTicks = [0, 20, 40, 60, 80, 100]
  const xTicks = [0, 4, 9, 14, 19]

  return (
    <div style={{ padding: '24px 28px' }}>
      <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: 16 }}>
        CMC — {nProbes?.toLocaleString()} probes vs {nGallery?.toLocaleString()}-subject gallery
      </div>
      <svg width="100%" viewBox={`0 0 ${W} ${H}`} style={{ display: 'block', overflow: 'visible' }}>
        {yTicks.map(v => (
          <g key={v}>
            <line x1={pad.left} x2={pad.left + iW} y1={yS(v / 100)} y2={yS(v / 100)}
              stroke="rgba(255,255,255,0.04)" strokeWidth={1} />
            <text x={pad.left - 9} y={yS(v / 100) + 4} textAnchor="end"
              fill="rgba(125,159,194,0.6)" fontSize={10} fontFamily="Inter,sans-serif">
              {v}%
            </text>
          </g>
        ))}
        {xTicks.map(i => (
          <g key={i}>
            <line x1={xS(i)} x2={xS(i)} y1={pad.top} y2={pad.top + iH}
              stroke="rgba(255,255,255,0.04)" strokeWidth={1} />
            <text x={xS(i)} y={pad.top + iH + 16} textAnchor="middle"
              fill="rgba(125,159,194,0.6)" fontSize={10} fontFamily="Inter,sans-serif">
              {i + 1}
            </text>
          </g>
        ))}
        <defs>
          <linearGradient id="cmc-area" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#00d4ff" stopOpacity={0.15} />
            <stop offset="100%" stopColor="#00d4ff" stopOpacity={0.01} />
          </linearGradient>
        </defs>
        <polygon points={areaPoints} fill="url(#cmc-area)" />
        <polyline points={linePoints} fill="none" stroke="#00d4ff" strokeWidth={2.5} strokeLinejoin="round" />
        {rankK.map((v, i) => (
          <circle key={i} cx={xS(i)} cy={yS(v)} r={i === 0 ? 6 : 3.5}
            fill="#00d4ff" stroke={i === 0 ? 'rgba(0,212,255,0.25)' : 'none'}
            strokeWidth={i === 0 ? 7 : 0} opacity={0.95} />
        ))}
        <text x={xS(0) + 11} y={yS(rankK[0]) - 9}
          fill="#00d4ff" fontSize={11} fontWeight={800} fontFamily="Inter,sans-serif">
          {(rankK[0] * 100).toFixed(1)}%
        </text>
        <text x={pad.left + iW / 2} y={H - 5} textAnchor="middle"
          fill="rgba(125,159,194,0.55)" fontSize={11} fontFamily="Inter,sans-serif">
          Rank
        </text>
        <text x={14} y={pad.top + iH / 2} textAnchor="middle"
          fill="rgba(125,159,194,0.55)" fontSize={11} fontFamily="Inter,sans-serif"
          transform={`rotate(-90,14,${pad.top + iH / 2})`}>
          Identification Rate (%)
        </text>
      </svg>
    </div>
  )
}

function RobustnessChart({ perturbations }) {
  const W = 520, H = 290
  const pad = { top: 24, right: 24, bottom: 52, left: 58 }
  const iW = W - pad.left - pad.right
  const iH = H - pad.top - pad.bottom
  const entries = Object.entries(perturbations)
  const maxLen  = Math.max(...entries.map(([, rows]) => rows.length))
  const xS = (i, n) => pad.left + (n > 1 ? (i / (n - 1)) * iW : iW / 2)
  const yS = v => pad.top + iH - v * iH
  const yTicks = [0, 20, 40, 60, 80, 100]

  return (
    <div>
      <div style={{ padding: '16px 22px', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
        <span style={{ fontSize: 10, fontWeight: 800, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--text-muted)' }}>
          Match Rate vs Degradation Severity
        </span>
      </div>
      <div style={{ padding: '16px' }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px 18px', marginBottom: 14 }}>
          {entries.map(([name], ci) => (
            <div key={name} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span style={{ width: 22, height: 3, borderRadius: 2, background: COLORS[ci % 5], display: 'inline-block' }} />
              <span style={{ fontSize: 10, color: 'rgba(125,159,194,0.8)', fontFamily: 'Inter,sans-serif' }}>{name}</span>
            </div>
          ))}
        </div>
        <svg width="100%" viewBox={`0 0 ${W} ${H}`} style={{ display: 'block', overflow: 'visible' }}>
          {yTicks.map(v => (
            <g key={v}>
              <line x1={pad.left} x2={pad.left + iW} y1={yS(v / 100)} y2={yS(v / 100)}
                stroke="rgba(255,255,255,0.04)" strokeWidth={1} />
              <text x={pad.left - 9} y={yS(v / 100) + 4} textAnchor="end"
                fill="rgba(125,159,194,0.6)" fontSize={10} fontFamily="Inter,sans-serif">{v}%</text>
            </g>
          ))}
          {Array.from({ length: maxLen }, (_, i) => (
            <text key={i} x={xS(i, maxLen)} y={pad.top + iH + 16} textAnchor="middle"
              fill="rgba(125,159,194,0.6)" fontSize={10} fontFamily="Inter,sans-serif">{i}</text>
          ))}
          {entries.map(([name, rows], ci) => {
            const color = COLORS[ci % 5]
            const pts = rows.map((row, i) => `${xS(i, rows.length)},${yS(row.match_rate)}`).join(' ')
            return <polyline key={name} points={pts} fill="none" stroke={color} strokeWidth={2.2} strokeLinejoin="round" opacity={0.88} />
          })}
          {entries.map(([name, rows], ci) =>
            rows.map((row, i) => (
              <circle key={`${name}-${i}`} cx={xS(i, rows.length)} cy={yS(row.match_rate)} r={3.5}
                fill={COLORS[ci % 5]} opacity={0.9} />
            ))
          )}
          <text x={pad.left + iW / 2} y={H - 5} textAnchor="middle"
            fill="rgba(125,159,194,0.55)" fontSize={11} fontFamily="Inter,sans-serif">Severity Step</text>
          <text x={14} y={pad.top + iH / 2} textAnchor="middle"
            fill="rgba(125,159,194,0.55)" fontSize={11} fontFamily="Inter,sans-serif"
            transform={`rotate(-90,14,${pad.top + iH / 2})`}>Match Rate (%)</text>
        </svg>
      </div>
    </div>
  )
}

function PlotImage({ src, title }) {
  return (
    <div style={{
      background: 'linear-gradient(145deg, rgba(20,30,56,0.96), rgba(14,22,46,0.98))',
      border: '1px solid rgba(255,255,255,0.06)',
      borderRadius: 14, overflow: 'hidden',
    }}>
      <div style={{ padding: '12px 18px', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
        <span style={{ fontSize: 9.5, fontWeight: 800, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--text-muted)' }}>
          {title}
        </span>
      </div>
      <img src={src} alt={title} style={{ width: '100%', display: 'block', background: '#060d1a' }} />
    </div>
  )
}

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

export default function Metrics() {
  const [data, setData]       = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState('')

  async function load() {
    setLoading(true); setError('')
    try { setData(await getMetrics()) }
    catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  const m = data?.id_metrics
  const r = data?.robustness

  const STAT_CARDS = m ? [
    { label: `Rank-1 (${(m.n_gallery / 1000).toFixed(0)}k gallery)`, val: `${(m.rank_1 * 100).toFixed(2)}%`, color: 'var(--accent)', glow: 'rgba(0,229,255,0.5)', topBorder: '#00e5ff' },
    { label: 'Rank-5',      val: `${(m.rank_5  * 100).toFixed(2)}%`, color: '#a855f7', glow: 'rgba(168,85,247,0.5)', topBorder: '#a855f7' },
    { label: 'Rank-10',     val: `${(m.rank_10 * 100).toFixed(2)}%`, color: 'var(--success)', glow: 'rgba(16,185,129,0.5)', topBorder: '#10b981' },
    { label: 'Probe images', val: m.n_probes?.toLocaleString(),       color: 'var(--text-sec)', glow: 'rgba(125,159,194,0.4)', topBorder: '#7d9fc2' },
  ] : []

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
            LFW · FairFace 3k gallery
          </div>
          <h2 style={{
            fontSize: 40, fontWeight: 900, letterSpacing: '-0.03em',
            background: 'linear-gradient(135deg, var(--text-pri) 0%, var(--accent) 100%)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text',
            marginBottom: 8,
          }}>Identification Metrics</h2>
          <p className="section-sub" style={{ fontSize: 16 }}>
            CMC curve · 1:N gallery search · robustness under image degradation
          </p>
        </div>
        <button className={data ? 'btn-ghost' : 'btn-primary'} onClick={load} disabled={loading}>
          {loading
            ? <><span className="spin" style={{ marginRight: 8 }}>◌</span>Loading…</>
            : data ? '↻ Refresh' : '◉  Load Results'
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

      {!data && !loading && (
        <div style={{
          textAlign: 'center', padding: '90px 20px',
          border: '1px dashed rgba(255,255,255,0.07)', borderRadius: 20,
          color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 20,
        }}>
          <div style={{
            width: 80, height: 80, borderRadius: '50%',
            border: '1px solid rgba(0,229,255,0.1)',
            background: 'rgba(0,229,255,0.02)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 34, color: 'rgba(0,229,255,0.18)',
          }}>◉</div>
          <div>
            <div style={{ fontSize: 16, fontWeight: 600, color: 'var(--text-sec)', marginBottom: 6 }}>
              No metrics loaded
            </div>
            <div style={{ fontSize: 13 }}>Click "Load Results" to pull identification metrics</div>
          </div>
        </div>
      )}

      {m && (
        <>
          {/* Stat cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 16, marginBottom: 32 }}>
            {STAT_CARDS.map(c => (
              <div key={c.label} style={{
                background: 'linear-gradient(145deg, rgba(22,34,62,0.96), rgba(14,22,46,0.98))',
                border: '1px solid rgba(255,255,255,0.07)',
                borderTop: `2px solid ${c.topBorder}`,
                borderRadius: 16, padding: '24px 18px', textAlign: 'center',
                position: 'relative', overflow: 'hidden',
                transition: 'all 0.25s ease',
              }}
              onMouseEnter={e => {
                e.currentTarget.style.transform = 'translateY(-4px)'
                e.currentTarget.style.boxShadow = `0 16px 48px ${c.glow}22`
              }}
              onMouseLeave={e => {
                e.currentTarget.style.transform = ''
                e.currentTarget.style.boxShadow = ''
              }}>
                <div style={{
                  position: 'absolute', top: 0, left: '10%', right: '10%', height: 1,
                  background: `linear-gradient(90deg, transparent, ${c.topBorder}55, transparent)`,
                }} />
                <div style={{
                  fontSize: 38, fontWeight: 900, color: c.color, marginBottom: 10,
                  fontFamily: "'Orbitron','Inter',sans-serif",
                  textShadow: `0 0 26px ${c.glow}`,
                  letterSpacing: '-0.02em',
                }}>{c.val}</div>
                <div style={{ fontSize: 9.5, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)' }}>
                  {c.label}
                </div>
              </div>
            ))}
          </div>

          <SectionDivider label="CMC Curve" />
          <div style={{
            background: 'linear-gradient(145deg, rgba(20,30,56,0.96), rgba(14,22,46,0.98))',
            border: '1px solid rgba(255,255,255,0.07)',
            borderRadius: 16, overflow: 'hidden', marginBottom: 32,
          }}>
            <CmcChart rankK={m.rank_k} nProbes={m.n_probes} nGallery={m.n_gallery} />
          </div>

          <SectionDivider label="Verification Curves" />
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 32 }}>
            <PlotImage src="/api/plots/lfw_roc.png"                title="ROC Curve — LFW" />
            <PlotImage src="/api/plots/lfw_det.png"                title="DET Curve — LFW" />
            <PlotImage src="/api/plots/lfw_score_distributions.png" title="Score Distributions — Genuine vs Impostor" />
            <PlotImage src="/api/plots/lfw_cmc.png"                title="CMC Curve — LFW (static)" />
          </div>

          {r?.perturbations && (
            <>
              <SectionDivider label="Robustness Analysis" />
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
                <div style={{
                  background: 'linear-gradient(145deg, rgba(20,30,56,0.96), rgba(14,22,46,0.98))',
                  border: '1px solid rgba(255,255,255,0.07)',
                  borderRadius: 16, overflow: 'hidden',
                }}>
                  <RobustnessChart perturbations={r.perturbations} />
                </div>

                <div style={{
                  background: 'linear-gradient(145deg, rgba(20,30,56,0.96), rgba(14,22,46,0.98))',
                  border: '1px solid rgba(255,255,255,0.07)',
                  borderRadius: 16, overflow: 'hidden',
                }}>
                  <div style={{ padding: '16px 22px', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                    <span style={{ fontSize: 10, fontWeight: 800, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                      Degradation Summary
                    </span>
                  </div>
                  <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                      <thead>
                        <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                          {['Perturbation', 'Baseline', 'Worst', 'Drop'].map(h => (
                            <th key={h} style={{
                              padding: '10px 16px', fontSize: 9, fontWeight: 800,
                              textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--text-muted)',
                              textAlign: h === 'Perturbation' ? 'left' : 'center',
                              background: 'rgba(0,0,0,0.2)',
                            }}>{h}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {Object.entries(r.perturbations).map(([name, rows], i) => {
                          const base  = rows[0].match_rate * 100
                          const worst = Math.min(...rows.map(row => row.match_rate)) * 100
                          const drop  = base - worst
                          const lineColor = COLORS[i % 5]
                          return (
                            <tr key={name} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                              <td style={{ padding: '12px 16px', color: 'var(--text-pri)', fontWeight: 600 }}>
                                <span style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
                                  <span style={{ width: 8, height: 8, borderRadius: '50%', background: lineColor, flexShrink: 0, boxShadow: `0 0 6px ${lineColor}` }} />
                                  {name}
                                </span>
                              </td>
                              <td style={{ padding: '12px 16px', textAlign: 'center', color: 'var(--accent)', fontWeight: 700 }}>
                                {base.toFixed(1)}%
                              </td>
                              <td style={{ padding: '12px 16px', textAlign: 'center', fontWeight: 700, color: drop > 20 ? 'var(--danger)' : drop > 5 ? 'var(--warning)' : 'var(--success)' }}>
                                {worst.toFixed(1)}%
                              </td>
                              <td style={{ padding: '12px 16px', textAlign: 'center' }}>
                                <span className={`tag ${drop > 20 ? 'tag-fail' : drop > 5 ? 'tag-warn' : 'tag-pass'}`}>
                                  −{drop.toFixed(1)} pp
                                </span>
                              </td>
                            </tr>
                          )
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </>
          )}
        </>
      )}
    </div>
  )
}
