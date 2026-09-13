import { useState } from 'react'
import { generateReport } from '../api'

const STEPS = [
  { label: 'Ethics Officer analysing fairness report…', pct: 15 },
  { label: 'Building compliance summary…', pct: 45 },
  { label: 'Generating PDF with charts…', pct: 75 },
  { label: 'Finalising document…', pct: 92 },
  { label: 'Done', pct: 100 },
]

const REPORT_SECTIONS = [
  { icon: '◈', label: 'Executive Summary', desc: 'High-level system overview and key findings' },
  { icon: '⚖', label: 'Methodology', desc: 'ArcFace embeddings, cosine similarity, FairFace 86k' },
  { icon: '◉', label: 'Fairness Findings', desc: 'FMRD ratios, disparate impact per demographic' },
  { icon: '▤', label: 'Compliance Verdict', desc: 'EU AI Act Annex IV assessment per axis' },
  { icon: '⊕', label: 'Mitigations', desc: 'Recommended corrective actions before deployment' },
  { icon: '◊', label: 'Annex IV Mapping', desc: 'Structured mapping to regulatory requirements' },
]

const SECTION_COLORS = [
  'rgba(0,229,255,', 'rgba(139,92,246,', 'rgba(16,185,129,',
  'rgba(245,158,11,', 'rgba(244,63,94,', 'rgba(240,171,252,',
]

export default function Report() {
  const [status, setStatus] = useState('idle')
  const [progress, setProgress] = useState(0)
  const [stepLabel, setStepLabel] = useState('')
  const [pdfUrl, setPdfUrl] = useState('')
  const [sizeKb, setSizeKb] = useState(0)
  const [fname, setFname] = useState('')
  const [error, setError] = useState('')

  async function generate() {
    setStatus('loading'); setError(''); setProgress(0)
    let stepIdx = 0
    const stepTimer = setInterval(() => {
      if (stepIdx < STEPS.length - 1) {
        setStepLabel(STEPS[stepIdx].label)
        setProgress(STEPS[stepIdx].pct)
        stepIdx++
      }
    }, 1400)
    try {
      const res = await generateReport()
      clearInterval(stepTimer)
      setProgress(100); setStepLabel('Complete')
      setPdfUrl(res.pdf_url); setSizeKb(res.size_kb); setFname(res.filename)
      setStatus('done')
    } catch (e) {
      clearInterval(stepTimer)
      setError(e.message); setStatus('error')
    }
  }

  return (
    <div style={{ maxWidth: 960, margin: '0 auto', padding: '48px 28px 60px' }}>
      {/* Header */}
      <div style={{ marginBottom: 40 }}>
        <div className="page-eyebrow">
          <span style={{
            display: 'inline-block', width: 5, height: 5, borderRadius: '50%',
            background: 'var(--accent)', animation: 'dot-pulse 2s ease-in-out infinite',
          }}/>
          EU AI Act · Annex IV
        </div>
        <h2 style={{
          fontSize: 40, fontWeight: 900, letterSpacing: '-0.03em',
          background: 'linear-gradient(135deg, var(--text-pri) 0%, #a855f7 100%)',
          WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text',
          marginBottom: 8,
        }}>Compliance Report</h2>
        <p className="section-sub" style={{ fontSize: 16 }}>
          Generates a full audit PDF — AI ethics analysis, fairness charts, regulator-ready format
        </p>
      </div>

      {status !== 'done' && (
        <div style={{
          background: 'linear-gradient(145deg, rgba(22,34,62,0.94), rgba(14,22,46,0.98))',
          border: '1px solid rgba(255,255,255,0.07)',
          borderRadius: 22, padding: '52px 36px', textAlign: 'center',
          marginBottom: 28, position: 'relative', overflow: 'hidden',
        }}>
          {/* Background glow */}
          <div style={{
            position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%,-50%)',
            width: 500, height: 500, borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(139,92,246,0.05) 0%, transparent 65%)',
            pointerEvents: 'none',
          }}/>

          {status === 'idle' && (
            <>
              <div style={{
                display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 14,
                marginBottom: 44, maxWidth: 620, margin: '0 auto 44px',
              }}>
                {REPORT_SECTIONS.map((s, i) => {
                  const color = SECTION_COLORS[i % SECTION_COLORS.length]
                  return (
                    <div key={s.label} style={{
                      padding: '18px 16px',
                      background: `${color}0.04)`,
                      border: `1px solid ${color}0.12)`,
                      borderRadius: 14, textAlign: 'center',
                    }}>
                      <div style={{
                        width: 40, height: 40, borderRadius: 12,
                        background: `${color}0.1)`, border: `1px solid ${color}0.2)`,
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: 18, margin: '0 auto 10px',
                        color: `${color}1)`,
                      }}>{s.icon}</div>
                      <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-pri)', marginBottom: 4 }}>
                        {s.label}
                      </div>
                      <div style={{ fontSize: 10, color: 'var(--text-muted)', lineHeight: 1.5 }}>
                        {s.desc}
                      </div>
                    </div>
                  )
                })}
              </div>

              <button className="btn-primary" onClick={generate}
                style={{ padding: '17px 52px', fontSize: 13, letterSpacing: '0.12em' }}>
                ▤  Generate PDF Report
              </button>
              <div style={{ marginTop: 16, fontSize: 12, color: 'var(--text-muted)' }}>
                Takes ~15 seconds · Calls Ethics Officer API · Embeds Plotly charts
              </div>
            </>
          )}

          {status === 'loading' && (
            <div style={{ maxWidth: 500, margin: '0 auto' }}>
              <div style={{ position: 'relative', width: 80, height: 80, margin: '0 auto 32px' }}>
                <div style={{
                  position: 'absolute', inset: 0, borderRadius: '50%',
                  border: '2px solid rgba(0,229,255,0.1)',
                  borderTopColor: 'var(--accent)',
                  animation: 'spin 1s linear infinite',
                  boxShadow: '0 0 32px rgba(0,229,255,0.2)',
                }}/>
                <div style={{
                  position: 'absolute', inset: 12, borderRadius: '50%',
                  border: '2px solid rgba(139,92,246,0.08)',
                  borderTopColor: '#a855f7',
                  animation: 'spin 1.6s linear infinite reverse',
                }}/>
              </div>
              <div style={{
                fontSize: 15, color: 'var(--accent)', fontWeight: 600,
                marginBottom: 28, minHeight: 24, letterSpacing: '0.02em',
              }}>
                {stepLabel || 'Initialising…'}
              </div>
              <div style={{
                height: 8, background: 'rgba(255,255,255,0.05)',
                borderRadius: 4, overflow: 'hidden', marginBottom: 10,
              }}>
                <div style={{
                  width: `${progress}%`, height: '100%',
                  background: 'linear-gradient(90deg, var(--accent), #a855f7)',
                  borderRadius: 4, transition: 'width 0.9s cubic-bezier(0.4,0,0.2,1)',
                  boxShadow: '0 0 20px rgba(0,229,255,0.5)',
                  position: 'relative', overflow: 'hidden',
                }}>
                  <div style={{
                    position: 'absolute', inset: 0,
                    background: 'linear-gradient(105deg, transparent 40%, rgba(255,255,255,0.25) 50%, transparent 60%)',
                    animation: 'shimmer 1.5s ease-in-out infinite',
                  }}/>
                </div>
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)', letterSpacing: '0.04em' }}>
                {progress}% complete
              </div>
            </div>
          )}

          {status === 'error' && (
            <>
              <div style={{
                width: 68, height: 68, borderRadius: '50%', margin: '0 auto 22px',
                background: 'rgba(244,63,94,0.1)', border: '1px solid rgba(244,63,94,0.3)',
                display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 28,
                color: 'var(--danger)',
              }}>✗</div>
              <div style={{ color: 'var(--danger)', marginBottom: 28, fontSize: 14 }}>{error}</div>
              <button className="btn-primary" onClick={generate} style={{ padding: '14px 36px' }}>
                ↻ Retry
              </button>
            </>
          )}
        </div>
      )}

      {status === 'done' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          <div style={{
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            padding: '20px 24px',
            background: 'linear-gradient(135deg, rgba(16,185,129,0.06), rgba(16,185,129,0.03))',
            border: '1px solid rgba(16,185,129,0.28)',
            borderRadius: 16, boxShadow: '0 0 48px rgba(16,185,129,0.07)',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
              <div style={{
                width: 40, height: 40, borderRadius: 12,
                background: 'rgba(16,185,129,0.15)', border: '1px solid rgba(16,185,129,0.35)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 18, color: 'var(--success)',
                boxShadow: '0 0 20px rgba(16,185,129,0.2)',
              }}>✓</div>
              <div>
                <div style={{ color: 'var(--text-pri)', fontWeight: 700, fontSize: 14 }}>{fname}</div>
                <div style={{ color: 'var(--text-muted)', fontSize: 12, marginTop: 2 }}>{sizeKb} KB · PDF</div>
              </div>
            </div>
            <div style={{ display: 'flex', gap: 12 }}>
              <a href={pdfUrl} download={fname} className="btn-ghost"
                style={{ textDecoration: 'none', padding: '10px 20px', fontSize: 11 }}>
                ⬇ Download
              </a>
              <button className="btn-primary" onClick={generate} style={{ fontSize: 11, padding: '10px 20px' }}>
                ↻ Regenerate
              </button>
            </div>
          </div>

          <div style={{
            borderRadius: 18, overflow: 'hidden',
            border: '1px solid rgba(255,255,255,0.07)',
            boxShadow: '0 24px 80px rgba(0,0,0,0.6)',
          }}>
            <iframe
              src={pdfUrl}
              width="100%" height="860"
              style={{ display: 'block', background: '#fff', border: 'none' }}
              title="Compliance Report"
            />
          </div>
        </div>
      )}
    </div>
  )
}
