import { useState, useEffect } from 'react'

const METRICS = [
  { num: '99.70', suf: '%',  label: 'LFW Accuracy',    sub: 'Face verification',  color: '#00e5ff', rgb: '0,229,255',   tag: null   },
  { num: '0.30',  suf: '%',  label: 'Equal Error Rate', sub: 'EER at τ = 0.181',  color: '#10b981', rgb: '16,185,129',  tag: null   },
  { num: '9.19',  suf: '×',  label: 'Race FMRD',        sub: 'Fairness disparity', color: '#f43f5e', rgb: '244,63,94',   tag: 'FAIL' },
  { num: '1.37',  suf: '×',  label: 'Gender FMRD',      sub: 'Fairness disparity', color: '#10b981', rgb: '16,185,129',  tag: 'PASS' },
  { num: '42.3',  suf: '×',  label: 'Age FMRD',         sub: 'Fairness disparity', color: '#f43f5e', rgb: '244,63,94',   tag: 'FAIL' },
]

const PIPELINE = [
  { n: '01', label: 'Face Input',     sub: 'JPEG · PNG',    color: '#00e5ff' },
  { n: '02', label: 'RetinaFace',    sub: 'Detection',      color: '#a855f7' },
  { n: '03', label: 'ArcFace',       sub: '512-d embed',    color: '#00e5ff' },
  { n: '04', label: 'Cosine Match',  sub: 'τ = 0.181',      color: '#a855f7' },
  { n: '05', label: 'Fairness Audit',sub: 'FMRD · DI',      color: '#10b981' },
  { n: '06', label: 'EU AI Report',  sub: 'Annex IV',       color: '#f59e0b' },
]

const HIGHLIGHTS = [
  { icon: '◈', val: '99.70%',  label: 'LFW Acc',    color: '#00e5ff' },
  { icon: '⚖', val: '2 / 3',  label: 'FMRD Fails', color: '#f43f5e' },
  { icon: '⊙', val: '299 FPS', label: 'PAD · M4',   color: '#10b981' },
  { icon: '▤', val: 'Annex IV',label: 'EU AI Act',  color: '#fbbf24' },
]

const TICKER_ITEMS = [
  '◈ ArcFace buffalo_l · Cosine Sim: 0.7834',
  '⊙ RetinaFace Detection · Confidence: 1.000',
  '⚖ Race FMRD: 9.19× · HIGH RISK',
  '◉ Processing: 299 FPS · M4 Neural Engine',
  '▤ EU AI Act · Annex IV · Risk: HIGH',
  '⚖ Gender FMR Female: 1.82% · Male: 1.33%',
  '◈ LFW Accuracy: 99.70% · EER: 0.30%',
  '⚖ Age 0–12 FMR: 15.3% · Age 25–50: 0.36%',
  '⊕ Enrollment DB: 1,024 subjects · M4',
  '◊ Claude Sonnet 4.6 · Ethics AI · Active',
]

function useCount(target, duration = 1600) {
  const [val, setVal] = useState(0)
  const [done, setDone] = useState(false)
  useEffect(() => {
    let raf
    const t0 = performance.now()
    const n = parseFloat(target)
    const tick = ts => {
      const p = Math.min((ts - t0) / duration, 1)
      setVal(n * (1 - Math.pow(1 - p, 3)))
      if (p < 1) raf = requestAnimationFrame(tick)
      else setDone(true)
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [])
  return [val, done]
}

function Orbital() {
  return (
    <div style={{ position: 'relative', width: 260, height: 260, flexShrink: 0 }}>
      {/* Expanding pulse rings */}
      {[0, 1, 2].map(i => (
        <div key={i} style={{
          position: 'absolute', inset: -8,
          borderRadius: '50%',
          border: '1px solid rgba(0,229,255,0.22)',
          animation: `pulse-ring ${3.2}s ease-out ${i * 1.07}s infinite`,
          pointerEvents: 'none',
        }}/>
      ))}

      {/* Outer halo glow */}
      <div style={{
        position: 'absolute', inset: -48, borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(124,58,237,0.18) 0%, rgba(0,229,255,0.07) 45%, transparent 70%)',
        pointerEvents: 'none',
      }}/>

      {/* Ring 1 — fast */}
      <div style={{
        position: 'absolute', inset: 0, borderRadius: '50%',
        background: 'conic-gradient(from 0deg, #00e5ff, #7c3aed, #f0abfc, #10b981, #f59e0b, #00e5ff)',
        animation: 'spin 9s linear infinite', opacity: 0.95,
      }}/>
      <div style={{ position: 'absolute', inset: 5, borderRadius: '50%', background: '#0e1d36' }}/>

      {/* Ring 2 — counter */}
      <div style={{
        position: 'absolute', inset: 18, borderRadius: '50%',
        background: 'conic-gradient(from 60deg, #a855f7, #00e5ff, #f59e0b, #a855f7)',
        animation: 'spin 17s linear infinite reverse', opacity: 0.52,
      }}/>
      <div style={{ position: 'absolute', inset: 23, borderRadius: '50%', background: '#0e1d36' }}/>

      {/* Ring 3 — slow */}
      <div style={{
        position: 'absolute', inset: 37, borderRadius: '50%',
        background: 'conic-gradient(from 180deg, #00e5ff, #a855f7, #00e5ff)',
        animation: 'spin 26s linear infinite', opacity: 0.3,
      }}/>
      <div style={{ position: 'absolute', inset: 41, borderRadius: '50%', background: '#0e1d36' }}/>

      {/* Center */}
      <div style={{
        position: 'absolute', inset: 0,
        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 7,
      }}>
        <div style={{
          fontSize: 58, fontWeight: 900, lineHeight: 1,
          fontFamily: "'Orbitron', sans-serif",
          background: 'linear-gradient(135deg, #00e5ff 30%, #a855f7)',
          WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text',
          filter: 'drop-shadow(0 0 28px rgba(0,229,255,0.75))',
          animation: 'text-flicker 12s ease-in-out infinite',
        }}>◈</div>
        <div style={{
          fontSize: 7.5, fontWeight: 900, letterSpacing: '0.32em', textTransform: 'uppercase',
          color: 'rgba(0,229,255,0.7)', textShadow: '0 0 14px rgba(0,229,255,0.5)',
        }}>ETHOS</div>
      </div>

      {/* Orbiting dot — cyan, fast */}
      <div style={{ position: 'absolute', inset: 0, animation: 'spin 4s linear infinite' }}>
        <div style={{
          position: 'absolute', top: -6, left: '50%', transform: 'translateX(-50%)',
          width: 12, height: 12, borderRadius: '50%',
          background: '#00e5ff', boxShadow: '0 0 18px #00e5ff, 0 0 36px rgba(0,229,255,0.55)',
        }}/>
      </div>
      {/* Orbiting dot — violet, slower reverse */}
      <div style={{ position: 'absolute', inset: 0, animation: 'spin 7s linear infinite reverse' }}>
        <div style={{
          position: 'absolute', bottom: -5, left: '50%', transform: 'translateX(-50%)',
          width: 8, height: 8, borderRadius: '50%',
          background: '#a855f7', boxShadow: '0 0 14px #a855f7, 0 0 28px rgba(168,85,247,0.6)',
        }}/>
      </div>
      {/* Orbiting dot — amber, medium */}
      <div style={{ position: 'absolute', inset: 0, animation: 'spin 5.5s linear infinite' }}>
        <div style={{
          position: 'absolute', top: '50%', right: -5, transform: 'translateY(-50%)',
          width: 7, height: 7, borderRadius: '50%',
          background: '#f59e0b', boxShadow: '0 0 12px #f59e0b, 0 0 22px rgba(245,158,11,0.55)',
        }}/>
      </div>
      {/* Orbiting dot — green */}
      <div style={{ position: 'absolute', inset: 8, animation: 'spin 11s linear infinite reverse' }}>
        <div style={{
          position: 'absolute', top: '50%', left: -4, transform: 'translateY(-50%)',
          width: 5, height: 5, borderRadius: '50%',
          background: '#10b981', boxShadow: '0 0 10px #10b981, 0 0 20px rgba(16,185,129,0.5)',
        }}/>
      </div>
    </div>
  )
}

function MetricCard({ num, suf, label, sub, color, rgb, tag, index }) {
  const [animated, done] = useCount(num, 1600)
  const decimals = num.includes('.') ? num.split('.')[1].length : 0
  const display = animated.toFixed(decimals)
  const c = a => `rgba(${rgb},${a})`
  const isFail = tag === 'FAIL'

  return (
    <div
      style={{
        background: `radial-gradient(ellipse at top left, ${c(0.14)} 0%, rgba(9,18,34,0.97) 65%)`,
        border: `1px solid ${c(0.24)}`,
        borderTop: `2px solid ${c(isFail ? 0.9 : 0.75)}`,
        borderRadius: 16,
        padding: '20px 22px 18px',
        display: 'flex', flexDirection: 'column', gap: 10,
        transition: 'transform 0.25s cubic-bezier(0.34,1.56,0.64,1), box-shadow 0.25s ease',
        cursor: 'default',
        animation: `card-in 0.55s cubic-bezier(0.34,1.56,0.64,1) ${0.1 + index * 0.1}s both${isFail ? ', danger-pulse 3s ease-in-out 1.8s infinite' : ''}`,
        position: 'relative', overflow: 'hidden',
      }}
      onMouseEnter={e => {
        e.currentTarget.style.transform = 'translateY(-8px) scale(1.02)'
        e.currentTarget.style.boxShadow = `0 24px 56px ${c(0.28)}, 0 0 48px ${c(0.12)}, 0 0 0 1px ${c(0.35)}`
      }}
      onMouseLeave={e => {
        e.currentTarget.style.transform = ''
        e.currentTarget.style.boxShadow = ''
      }}
    >
      {/* Inner glow sweep on hover */}
      <div style={{
        position: 'absolute', inset: 0, borderRadius: 16,
        background: `radial-gradient(ellipse at 50% 0%, ${c(0.08)} 0%, transparent 60%)`,
        pointerEvents: 'none',
      }}/>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 6 }}>
        <div style={{ fontSize: 9, fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', color, opacity: 0.8 }}>
          {label}
        </div>
        {tag && (
          <span style={{
            fontSize: 7.5, fontWeight: 800, letterSpacing: '0.1em', flexShrink: 0,
            color: tag === 'PASS' ? '#10b981' : '#f43f5e',
            background: tag === 'PASS' ? 'rgba(16,185,129,0.12)' : 'rgba(244,63,94,0.16)',
            border: `1px solid ${tag === 'PASS' ? 'rgba(16,185,129,0.42)' : 'rgba(244,63,94,0.5)'}`,
            borderRadius: 4, padding: '2px 7px',
            animation: isFail ? 'glow-pulse 2s ease-in-out infinite' : undefined,
          }}>{tag}</span>
        )}
      </div>

      <div style={{
        fontSize: 42, fontWeight: 900, color, lineHeight: 1,
        fontFamily: "'Orbitron','Inter',sans-serif", letterSpacing: '-0.02em',
        textShadow: `0 0 ${done ? 28 : 8}px ${c(done ? 0.8 : 0.4)}`,
        fontVariantNumeric: 'tabular-nums',
        transition: 'text-shadow 0.8s ease',
        animation: done ? `number-settled 0.7s ease both` : undefined,
      }}>
        {display}<span style={{ fontSize: 18, opacity: 0.55, letterSpacing: 0 }}>{suf}</span>
      </div>

      <div style={{ fontSize: 10, color: 'var(--text-muted)', fontWeight: 500, letterSpacing: '0.02em' }}>{sub}</div>
    </div>
  )
}

function FlowConnector({ from, to, idx }) {
  return (
    <div style={{ width: 28, height: 52, display: 'flex', alignItems: 'center', flexShrink: 0 }}>
      <svg width="28" height="14" viewBox="0 0 28 14" fill="none" style={{ overflow: 'visible' }}>
        <defs>
          <linearGradient id={`fg${idx}`} x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor={from} stopOpacity="0.5"/>
            <stop offset="100%" stopColor={to} stopOpacity="0.5"/>
          </linearGradient>
        </defs>
        <line x1="0" y1="7" x2="28" y2="7" stroke={`url(#fg${idx})`} strokeWidth="1.5"/>
        <circle r="2.5" fill={from}>
          <animateMotion dur={`${1.0 + idx * 0.13}s`} repeatCount="indefinite">
            <mpath href={`#fp${idx}`}/>
          </animateMotion>
        </circle>
        <path id={`fp${idx}`} d="M 0 7 L 28 7" style={{ visibility: 'hidden' }}/>
      </svg>
    </div>
  )
}

function DataTicker() {
  const items = [...TICKER_ITEMS, ...TICKER_ITEMS]
  return (
    <div style={{
      overflow: 'hidden', height: 30,
      background: 'rgba(0,229,255,0.025)',
      borderTop: '1px solid rgba(0,229,255,0.07)',
      borderBottom: '1px solid rgba(0,229,255,0.07)',
      display: 'flex', alignItems: 'center',
      borderRadius: 8,
    }}>
      <div style={{
        display: 'flex', whiteSpace: 'nowrap',
        animation: 'ticker-scroll 35s linear infinite',
      }}>
        {items.map((item, i) => (
          <span key={i} style={{
            fontSize: 9, color: 'rgba(0,229,255,0.45)',
            fontFamily: 'monospace', letterSpacing: '0.06em',
            padding: '0 28px',
            borderRight: '1px solid rgba(0,229,255,0.08)',
          }}>
            {item}
          </span>
        ))}
      </div>
    </div>
  )
}

export default function Overview({ onNav }) {
  return (
    <>
      <style>{`
        @keyframes danger-pulse {
          0%,100% { box-shadow: none; }
          50% { box-shadow: 0 0 36px 3px rgba(244,63,94,0.18), inset 0 0 28px rgba(244,63,94,0.06); }
        }
      `}</style>

      <div style={{
        padding: '22px 44px 20px',
        display: 'flex', flexDirection: 'column', gap: 16,
        maxWidth: 1240, margin: '0 auto', boxSizing: 'border-box',
      }}>

        {/* ── Hero ── */}
        <div style={{
          display: 'grid', gridTemplateColumns: '1fr auto', gap: 52, alignItems: 'center',
          padding: '32px 40px',
          background: 'radial-gradient(ellipse at 82% 0%, rgba(139,92,246,0.24) 0%, rgba(0,229,255,0.07) 35%, rgba(10,20,42,0.7) 65%)',
          border: '1px solid rgba(255,255,255,0.1)',
          borderRadius: 24, position: 'relative', overflow: 'hidden',
          boxShadow: '0 0 100px rgba(139,92,246,0.1), inset 0 1px 0 rgba(255,255,255,0.07)',
          animation: 'fade-up 0.5s ease both',
        }}>
          {/* Top-left corner glow */}
          <div style={{
            position: 'absolute', top: 0, left: 0, width: 260, height: 260,
            background: 'radial-gradient(circle at 0% 0%, rgba(0,229,255,0.08) 0%, transparent 60%)',
            pointerEvents: 'none', borderRadius: 22,
          }}/>

          {/* Scanning horizontal beam */}
          <div style={{
            position: 'absolute', left: 0, right: 0, height: 1,
            background: 'linear-gradient(90deg, transparent 0%, rgba(0,229,255,0.5) 30%, rgba(139,92,246,0.4) 70%, transparent 100%)',
            animation: 'hero-scan 7s ease-in-out 2s infinite',
            top: 0, pointerEvents: 'none',
          }}/>

          {/* Divider line */}
          <div style={{
            position: 'absolute', bottom: 0, left: '6%', right: '6%', height: 1,
            background: 'linear-gradient(90deg, transparent, rgba(0,229,255,0.2), rgba(124,58,237,0.2), transparent)',
            pointerEvents: 'none',
          }}/>

          <div>
            <div style={{
              display: 'inline-flex', alignItems: 'center', gap: 8,
              fontSize: 10, fontWeight: 700, letterSpacing: '0.14em', textTransform: 'uppercase',
              color: 'var(--accent)', background: 'rgba(0,229,255,0.07)',
              border: '1px solid rgba(0,229,255,0.22)', borderRadius: 20, padding: '5px 16px',
              marginBottom: 22, animation: 'badge-glow 3s ease-in-out infinite alternate',
            }}>
              <span style={{ width: 5, height: 5, borderRadius: '50%', background: 'var(--accent)', animation: 'dot-pulse 2s ease-in-out infinite', boxShadow: '0 0 6px var(--accent)', display: 'inline-block' }}/>
              Master's Thesis · UPEC Spring 2026
            </div>

            <div style={{
              fontSize: 'clamp(72px, 8vw, 110px)', fontWeight: 900, lineHeight: 0.92,
              fontFamily: "'Orbitron','Inter',system-ui,sans-serif",
              letterSpacing: '-0.02em', marginBottom: 18,
              background: 'linear-gradient(135deg, #00e5ff 0%, #a855f7 50%, #f0f6ff 100%)',
              WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text',
              animation: 'hero-glow 4s ease-in-out infinite alternate, text-flicker 18s ease-in-out 6s infinite',
            }}>ETHOS</div>

            <div style={{
              fontSize: 11, fontWeight: 700, letterSpacing: '0.22em', textTransform: 'uppercase',
              color: 'rgba(150,195,235,0.72)', marginBottom: 20,
              textShadow: '0 0 28px rgba(0,229,255,0.28)',
            }}>Ethical Trust &amp; Holistic Oversight System</div>

            <p style={{ fontSize: 15, color: 'var(--text-sec)', lineHeight: 1.8, maxWidth: 460, marginBottom: 30 }}>
              Facial biometric fairness auditor for EU AI Act compliance —
              measuring recognition accuracy across race, gender &amp; age.
            </p>

            {/* Highlight chips with individual accent colors */}
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {HIGHLIGHTS.map((h, i) => (
                <div key={h.label}
                  style={{
                    display: 'flex', alignItems: 'center', gap: 8,
                    background: `${h.color}0d`,
                    border: `1px solid ${h.color}35`,
                    borderRadius: 12, padding: '9px 16px',
                    transition: 'all 0.22s ease', cursor: 'default',
                    animation: `fade-up 0.4s ease ${0.35 + i * 0.08}s both`,
                  }}
                  onMouseEnter={e => {
                    e.currentTarget.style.borderColor = `${h.color}70`
                    e.currentTarget.style.background = `${h.color}18`
                    e.currentTarget.style.transform = 'translateY(-3px)'
                    e.currentTarget.style.boxShadow = `0 10px 28px ${h.color}22`
                  }}
                  onMouseLeave={e => {
                    e.currentTarget.style.borderColor = `${h.color}35`
                    e.currentTarget.style.background = `${h.color}0d`
                    e.currentTarget.style.transform = ''
                    e.currentTarget.style.boxShadow = ''
                  }}
                >
                  <span style={{ fontSize: 13, color: h.color, textShadow: `0 0 14px ${h.color}` }}>{h.icon}</span>
                  <span style={{ fontSize: 13, fontWeight: 800, color: '#f0f6ff' }}>{h.val}</span>
                  <span style={{ fontSize: 9.5, color: 'rgba(150,180,210,0.58)', fontWeight: 500 }}>{h.label}</span>
                </div>
              ))}
            </div>
          </div>

          <Orbital />
        </div>

        {/* ── Live data ticker ── */}
        <DataTicker />

        {/* ── Metric Cards ── */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 12 }}>
          {METRICS.map((m, i) => <MetricCard key={m.label} {...m} index={i} />)}
        </div>

        {/* ── Pipeline ── */}
        <div style={{
          background: 'rgba(8,16,32,0.65)', border: '1px solid rgba(0,229,255,0.08)',
          borderRadius: 16, padding: '20px 28px',
          animation: 'fade-up 0.5s ease 0.7s both',
        }}>
          <div style={{
            fontSize: 9, fontWeight: 800, letterSpacing: '0.2em', textTransform: 'uppercase',
            color: 'var(--text-muted)', marginBottom: 20, textAlign: 'center',
            display: 'flex', alignItems: 'center', gap: 14,
          }}>
            <div style={{ flex: 1, height: 1, background: 'linear-gradient(90deg, transparent, rgba(0,229,255,0.18))' }}/>
            System Pipeline
            <div style={{ flex: 1, height: 1, background: 'linear-gradient(90deg, rgba(0,229,255,0.18), transparent)' }}/>
          </div>
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'center' }}>
            {PIPELINE.map((step, i) => (
              <div key={step.n} style={{ display: 'flex', alignItems: 'flex-start' }}>
                <div style={{
                  display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10,
                  width: 110, flexShrink: 0,
                  animation: `card-in 0.45s ease ${0.8 + i * 0.08}s both`,
                }}>
                  <div
                    style={{
                      width: 52, height: 52, borderRadius: '50%',
                      background: `${step.color}14`,
                      border: `1.5px solid ${step.color}52`,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      boxShadow: `0 0 22px ${step.color}2a, inset 0 0 14px ${step.color}08`,
                      fontSize: 11, fontWeight: 900, color: step.color,
                      fontFamily: "'Orbitron', sans-serif", letterSpacing: '0.04em',
                      transition: 'box-shadow 0.2s ease, border-color 0.2s ease, transform 0.2s ease',
                      cursor: 'default',
                    }}
                    onMouseEnter={e => {
                      e.currentTarget.style.boxShadow = `0 0 40px ${step.color}60, inset 0 0 22px ${step.color}16`
                      e.currentTarget.style.borderColor = `${step.color}90`
                      e.currentTarget.style.transform = 'scale(1.12)'
                    }}
                    onMouseLeave={e => {
                      e.currentTarget.style.boxShadow = `0 0 22px ${step.color}2a, inset 0 0 14px ${step.color}08`
                      e.currentTarget.style.borderColor = `${step.color}52`
                      e.currentTarget.style.transform = ''
                    }}
                  >{step.n}</div>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: 11, fontWeight: 700, color: '#e0f7ff', lineHeight: 1.3, marginBottom: 3 }}>{step.label}</div>
                    <div style={{ fontSize: 9.5, color: step.color, fontWeight: 500, opacity: 0.65 }}>{step.sub}</div>
                  </div>
                </div>
                {i < PIPELINE.length - 1 && (
                  <FlowConnector from={step.color} to={PIPELINE[i + 1].color} idx={i} />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* ── Actions ── */}
        <div style={{
          display: 'flex', justifyContent: 'center', gap: 10, paddingBottom: 4,
          animation: 'fade-up 0.45s ease 1s both',
        }}>
          <button className="btn-primary" onClick={() => onNav('verify')}>Verify 1:1</button>
          <button className="btn-ghost"   onClick={() => onNav('identify')}>Identify 1:N</button>
          <button className="btn-ghost"   onClick={() => onNav('fairness')}>Fairness Audit</button>
          <button className="btn-ghost"   onClick={() => onNav('enroll')}>Enroll</button>
          <button
            onClick={() => onNav('report')}
            style={{
              background: 'linear-gradient(135deg, #7c3aed, #a855f7)', color: '#f0f6ff',
              fontWeight: 800, padding: '13px 32px', borderRadius: 10, border: 'none',
              cursor: 'pointer', fontSize: 12, letterSpacing: '0.08em', textTransform: 'uppercase',
              transition: 'all 0.22s ease', fontFamily: 'Inter, sans-serif',
              boxShadow: '0 0 24px rgba(124,58,237,0.44)',
              position: 'relative', overflow: 'hidden',
            }}
            onMouseEnter={e => {
              e.currentTarget.style.boxShadow = '0 0 44px rgba(168,85,247,0.72)'
              e.currentTarget.style.transform = 'translateY(-2px)'
            }}
            onMouseLeave={e => {
              e.currentTarget.style.boxShadow = '0 0 24px rgba(124,58,237,0.44)'
              e.currentTarget.style.transform = ''
            }}
          >
            Generate Report
          </button>
        </div>

      </div>
    </>
  )
}
