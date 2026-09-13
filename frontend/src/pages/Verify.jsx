import { useState, useCallback, useEffect } from 'react'
import { verifyFaces, explainResult } from '../api'

function ExplainModal({ explanation, explaining, onClose }) {
  useEffect(() => {
    const h = e => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', h)
    return () => window.removeEventListener('keydown', h)
  }, [onClose])

  return (
    <div onClick={onClose} style={{
      position: 'fixed', inset: 0, zIndex: 9000,
      background: 'rgba(10,18,38,0.82)',
      backdropFilter: 'blur(16px)', WebkitBackdropFilter: 'blur(16px)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24,
    }}>
      <div onClick={e => e.stopPropagation()} style={{
        width: '100%', maxWidth: 560,
        background: 'linear-gradient(160deg, rgba(24,34,64,0.99), rgba(16,25,50,0.99))',
        border: '1px solid rgba(139,92,246,0.4)',
        borderRadius: 22,
        boxShadow: '0 0 100px rgba(139,92,246,0.22), 0 40px 100px rgba(0,0,0,0.7)',
        overflow: 'hidden',
        animation: 'verdict-in 0.3s ease both',
      }}>
        <div style={{
          padding: '20px 24px',
          borderBottom: '1px solid rgba(139,92,246,0.12)',
          background: 'rgba(139,92,246,0.05)',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{
              width: 36, height: 36, borderRadius: 12,
              background: 'linear-gradient(135deg, rgba(139,92,246,0.25), rgba(0,229,255,0.1))',
              border: '1px solid rgba(139,92,246,0.4)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 15, color: '#a855f7',
              boxShadow: '0 0 20px rgba(139,92,246,0.2)',
            }}>◊</div>
            <div>
              <div style={{ fontSize: 12, fontWeight: 800, letterSpacing: '0.1em', textTransform: 'uppercase', color: '#a855f7' }}>
                Claude · Refusal Analysis
              </div>
              <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 2, letterSpacing: '0.04em' }}>
                AI-generated explanation
              </div>
            </div>
          </div>
          <button onClick={onClose} style={{
            width: 30, height: 30, borderRadius: 8,
            background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)',
            color: 'var(--text-muted)', fontSize: 16, cursor: 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            transition: 'all 0.18s ease',
          }}
          onMouseEnter={e => { e.currentTarget.style.borderColor = 'rgba(255,255,255,0.25)'; e.currentTarget.style.color = 'var(--text-pri)' }}
          onMouseLeave={e => { e.currentTarget.style.borderColor = 'rgba(255,255,255,0.1)'; e.currentTarget.style.color = 'var(--text-muted)' }}>
            ✕
          </button>
        </div>

        <div style={{ padding: '28px 28px 32px' }}>
          {explaining ? (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16, padding: '20px 0' }}>
              <div style={{
                width: 36, height: 36, borderRadius: '50%',
                border: '2px solid rgba(139,92,246,0.2)',
                borderTopColor: '#a855f7',
                animation: 'spin 0.9s linear infinite',
              }}/>
              <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>Analysing refusal…</span>
            </div>
          ) : (
            <p style={{ fontSize: 14, color: 'var(--text-sec)', lineHeight: 1.8, margin: 0 }}>
              {explanation}
            </p>
          )}
        </div>

        {!explaining && (
          <div style={{
            padding: '14px 28px',
            borderTop: '1px solid rgba(139,92,246,0.1)',
            display: 'flex', justifyContent: 'flex-end',
          }}>
            <button onClick={onClose} className="btn-ghost" style={{ padding: '8px 24px', fontSize: 11 }}>
              Close
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

const DEFAULT_THRESHOLD = 0.1810

function DropZone({ label, slot, file, onFile }) {
  const [drag, setDrag] = useState(false)
  const preview = file ? URL.createObjectURL(file) : null

  const handleDrop = useCallback(e => {
    e.preventDefault(); setDrag(false)
    const f = e.dataTransfer.files[0]
    if (f && f.type.startsWith('image/')) onFile(f)
  }, [onFile])

  const borderColor = drag ? 'rgba(0,229,255,0.65)' : file ? 'rgba(0,229,255,0.32)' : 'rgba(0,229,255,0.1)'
  const bgColor = drag ? 'rgba(0,229,255,0.05)' : file ? 'rgba(16,25,50,0.97)' : 'rgba(12,22,46,0.75)'

  return (
    <label style={{
      display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
      gap: 14, cursor: 'pointer', borderRadius: 18, flex: 1,
      background: bgColor,
      position: 'relative', overflow: 'hidden',
      border: `1px solid ${borderColor}`,
      boxShadow: drag
        ? '0 0 80px rgba(0,229,255,0.18), inset 0 0 50px rgba(0,229,255,0.05)'
        : file ? '0 0 40px rgba(0,229,255,0.08)' : '0 0 0 rgba(0,0,0,0)',
      transition: 'all 0.3s ease',
    }}
    onDragOver={e => { e.preventDefault(); setDrag(true) }}
    onDragLeave={() => setDrag(false)}
    onDrop={handleDrop}>
      <input type="file" accept="image/*" style={{ display: 'none' }}
        onChange={e => e.target.files[0] && onFile(e.target.files[0])} />

      {/* Corner brackets — animated when idle */}
      {[['tl', 'top', 'left'], ['tr', 'top', 'right'], ['bl', 'bottom', 'left'], ['br', 'bottom', 'right']].map(([k, v, h]) => (
        <div key={k} style={{
          position: 'absolute',
          [v]: 14, [h]: 14,
          width: 24, height: 24,
          borderTop: v === 'top' ? `2px solid rgba(0,229,255,${file ? 0.65 : 0.35})` : 'none',
          borderBottom: v === 'bottom' ? `2px solid rgba(0,229,255,${file ? 0.65 : 0.35})` : 'none',
          borderLeft: h === 'left' ? `2px solid rgba(0,229,255,${file ? 0.65 : 0.35})` : 'none',
          borderRight: h === 'right' ? `2px solid rgba(0,229,255,${file ? 0.65 : 0.35})` : 'none',
          transition: 'border-color 0.4s ease',
          animation: !file ? 'glow-pulse 3s ease-in-out infinite' : undefined,
        }} />
      ))}

      {/* Idle slow scan line (always visible, very faint) */}
      {!file && (
        <div style={{
          position: 'absolute', left: 0, right: 0, height: 1,
          background: 'linear-gradient(90deg, transparent, rgba(0,229,255,0.18), transparent)',
          animation: 'hero-scan 5s ease-in-out infinite',
          top: 0, pointerEvents: 'none',
        }} />
      )}

      {/* Drag scan line (bright) */}
      {drag && (
        <div style={{
          position: 'absolute', left: 0, right: 0, height: 2,
          background: 'linear-gradient(90deg, transparent, var(--accent), transparent)',
          boxShadow: '0 0 24px var(--accent)',
          animation: 'scan-line 1.2s linear infinite',
          pointerEvents: 'none', top: 0,
        }} />
      )}

      <div style={{
        position: 'absolute', top: 14, left: '50%', transform: 'translateX(-50%)',
        fontSize: 9, fontWeight: 800, letterSpacing: '0.18em', textTransform: 'uppercase',
        color: file ? 'var(--accent)' : 'rgba(0,229,255,0.5)',
        background: 'rgba(8,16,36,0.85)',
        border: `1px solid ${file ? 'rgba(0,229,255,0.28)' : 'rgba(0,229,255,0.1)'}`,
        borderRadius: 6, padding: '3px 10px', whiteSpace: 'nowrap',
        backdropFilter: 'blur(10px)',
      }}>{slot} — {label}</div>

      {preview ? (
        <img src={preview} alt="preview" style={{
          maxWidth: '82%', maxHeight: '72%', borderRadius: 12,
          objectFit: 'contain', boxShadow: '0 16px 48px rgba(0,0,0,0.7)',
        }} />
      ) : (
        <div style={{ textAlign: 'center' }}>
          <div style={{
            width: 72, height: 72, borderRadius: 22,
            border: '1px solid rgba(0,229,255,0.18)',
            background: 'rgba(0,229,255,0.03)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 18px', fontSize: 28,
            color: 'rgba(0,229,255,0.3)',
            boxShadow: '0 0 32px rgba(0,229,255,0.06)',
            animation: 'float 5s ease-in-out infinite',
          }}>⊞</div>
          <div style={{ fontSize: 14, color: 'var(--text-muted)', fontWeight: 500, lineHeight: 1.7 }}>
            <span style={{ color: 'var(--accent)', fontWeight: 700 }}>Click to upload</span><br />
            <span style={{ fontSize: 12 }}>or drag &amp; drop</span>
          </div>
        </div>
      )}
    </label>
  )
}

export default function Verify() {
  const [fileA, setFileA] = useState(null)
  const [fileB, setFileB] = useState(null)
  const [threshold, setThreshold] = useState(DEFAULT_THRESHOLD)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [modalOpen, setModalOpen] = useState(false)
  const [explanation, setExplanation] = useState(null)
  const [explaining, setExplaining] = useState(false)

  async function handleVerify() {
    if (!fileA || !fileB) { setError('Upload both images first.'); return }
    setLoading(true); setError(''); setResult(null); setExplanation(null); setModalOpen(false)
    try { setResult(await verifyFaces(fileA, fileB, threshold)) }
    catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  async function handleExplain() {
    setModalOpen(true); setExplaining(true); setExplanation(null)
    try {
      const res = await explainResult('verify', { similarity: result.similarity, threshold: result.threshold })
      setExplanation(res.explanation)
    } catch (e) { setExplanation('Could not generate explanation: ' + e.message) }
    finally { setExplaining(false) }
  }

  const sim = result?.similarity ?? 0
  const match = result?.is_match
  const barPct = Math.max(0, Math.round(sim * 100))

  const matchGreen = 'rgba(16,185,129,'
  const failRed = 'rgba(244,63,94,'

  return (
    <>
    <div style={{
      height: 'calc(100vh - 104px)',
      padding: '16px 24px',
      display: 'grid',
      gridTemplateColumns: '320px 1fr',
      gap: 16,
      maxWidth: 1340,
      margin: '0 auto',
      boxSizing: 'border-box',
    }}>

      {/* ── LEFT: Controls ── */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12, minHeight: 0 }}>

        {/* Page header */}
        <div style={{ flexShrink: 0 }}>
          <div className="page-eyebrow">
            <span style={{
              width: 5, height: 5, borderRadius: '50%',
              background: 'var(--accent)',
              animation: 'dot-pulse 2s ease-in-out infinite',
              boxShadow: '0 0 6px var(--accent)',
              display: 'inline-block',
            }}/>
            1 : 1 Verification
          </div>
          <h2 style={{
            fontSize: 30, fontWeight: 900, letterSpacing: '-0.03em', lineHeight: 1.1, marginBottom: 4,
            background: 'linear-gradient(135deg, var(--text-pri) 0%, var(--accent) 100%)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text',
          }}>Face Verification</h2>
          <p style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.5 }}>
            ArcFace embeddings · cosine similarity
          </p>
        </div>

        {/* Threshold panel */}
        <div style={{
          background: 'linear-gradient(145deg, rgba(22,34,62,0.96), rgba(14,22,46,0.98))',
          border: '1px solid rgba(255,255,255,0.07)',
          borderTop: '2px solid rgba(0,229,255,0.55)',
          borderRadius: 14,
          padding: '20px',
          flexShrink: 0,
          boxShadow: '0 4px 32px rgba(0,0,0,0.4)',
        }}>
          <div style={{
            fontSize: 9, fontWeight: 800, letterSpacing: '0.18em', textTransform: 'uppercase',
            color: 'var(--text-muted)', marginBottom: 12,
          }}>Decision Threshold</div>

          <div style={{
            fontSize: 54, fontWeight: 900, fontFamily: "'Orbitron','Inter',sans-serif",
            letterSpacing: '-0.02em', lineHeight: 1, marginBottom: 4,
            background: 'linear-gradient(135deg, var(--accent), #a855f7)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text',
          }}>{threshold.toFixed(4)}</div>

          <div style={{ fontSize: 10, color: 'var(--text-muted)', marginBottom: 16 }}>
            EER-optimal ={' '}
            <span style={{ color: 'var(--accent)', fontWeight: 700 }}>{DEFAULT_THRESHOLD}</span>
          </div>

          <div style={{ position: 'relative' }}>
            <input type="range" min={0.05} max={0.95} step={0.005}
              value={threshold}
              onChange={e => setThreshold(parseFloat(e.target.value))}
              style={{ width: '100%', accentColor: 'var(--accent)', height: 4, outline: 'none', cursor: 'pointer' }} />
            <div style={{
              position: 'absolute', top: -8, left: `${((DEFAULT_THRESHOLD - 0.05) / 0.9) * 100}%`,
              transform: 'translateX(-50%)',
              width: 2, height: 12, borderRadius: 1, background: 'rgba(255,255,255,0.4)',
              pointerEvents: 'none',
            }} />
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8,
            fontSize: 9, color: 'var(--text-muted)', fontWeight: 600 }}>
            <span>0.05</span><span>0.95</span>
          </div>
        </div>

        {/* Result panel */}
        <div style={{
          flex: 1, minHeight: 0,
          background: result
            ? (match
              ? `linear-gradient(145deg, ${matchGreen}0.07) 0%, ${matchGreen}0.03) 100%)`
              : `linear-gradient(145deg, ${failRed}0.07) 0%, ${failRed}0.03) 100%)`)
            : 'linear-gradient(145deg, rgba(16,26,52,0.7), rgba(14,22,46,0.6))',
          border: `1px solid ${result ? (match ? 'rgba(16,185,129,0.32)' : 'rgba(244,63,94,0.32)') : 'rgba(255,255,255,0.06)'}`,
          borderRadius: 14,
          padding: 20,
          display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center',
          textAlign: 'center', position: 'relative', overflow: 'hidden',
          transition: 'all 0.4s ease',
          boxShadow: result
            ? (match ? '0 0 60px rgba(16,185,129,0.07)' : '0 0 60px rgba(244,63,94,0.07)')
            : 'none',
        }}>

          {result && (
            <>
              <div style={{
                position: 'absolute', top: '50%', left: '50%',
                transform: 'translate(-50%,-50%)',
                width: 260, height: 260, borderRadius: '50%',
                background: `radial-gradient(circle, ${match ? matchGreen + '0.1)' : failRed + '0.1)'} 0%, transparent 70%)`,
                pointerEvents: 'none',
              }} />

              <div style={{
                fontSize: 60, fontWeight: 900, fontFamily: "'Orbitron','Inter',sans-serif",
                letterSpacing: '0.04em', lineHeight: 1, marginBottom: 16,
                background: match
                  ? 'linear-gradient(135deg, #10b981, #34d399)'
                  : 'linear-gradient(135deg, #f43f5e, #f87171)',
                WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text',
                animation: 'verdict-in 0.4s ease both',
              }}>{match ? 'MATCH' : 'NO\nMATCH'}</div>

              <div style={{ width: '100%', marginBottom: 14 }}>
                <div style={{
                  height: 10, background: 'rgba(255,255,255,0.05)',
                  borderRadius: 5, overflow: 'visible', position: 'relative',
                }}>
                  <div style={{
                    width: `${barPct}%`, height: '100%', borderRadius: 5,
                    background: match
                      ? 'linear-gradient(90deg, #10b981, #34d399)'
                      : 'linear-gradient(90deg, #f43f5e, #f87171)',
                    boxShadow: `0 0 20px ${match ? 'rgba(16,185,129,0.55)' : 'rgba(244,63,94,0.55)'}`,
                    transition: 'width 0.7s cubic-bezier(0.4,0,0.2,1)',
                  }} />
                  <div style={{
                    position: 'absolute', top: -4, bottom: -4,
                    left: `${threshold * 100}%`, width: 2, borderRadius: 2,
                    background: 'rgba(255,255,255,0.45)',
                    boxShadow: '0 0 8px rgba(255,255,255,0.25)',
                  }}>
                    <div style={{
                      position: 'absolute', bottom: 12, left: '50%', transform: 'translateX(-50%)',
                      fontSize: 8, color: 'var(--text-muted)', whiteSpace: 'nowrap', fontWeight: 600,
                    }}>τ={threshold.toFixed(3)}</div>
                  </div>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 6,
                  fontSize: 9, color: 'var(--text-muted)' }}>
                  <span>0 · No match</span><span>1 · Identical</span>
                </div>
              </div>

              <div style={{ fontSize: 11, color: 'var(--text-sec)' }}>
                Similarity{' '}
                <span style={{
                  fontWeight: 900, color: 'var(--text-pri)',
                  fontFamily: "'Orbitron',sans-serif", fontSize: 14,
                  letterSpacing: '0.02em',
                }}>
                  {sim.toFixed(4)}
                </span>
                {' '}· τ = {threshold.toFixed(4)}
              </div>
            </>
          )}

          {!result && (
            <div>
              <div style={{
                width: 64, height: 64, borderRadius: '50%',
                border: '1px solid rgba(0,229,255,0.1)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 28, color: 'rgba(0,229,255,0.12)',
                margin: '0 auto 14px',
              }}>⟺</div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.7 }}>
                Upload two face images<br/>and run verification
              </div>
            </div>
          )}
        </div>

        {result && !match && (
          <button onClick={handleExplain} style={{
            flexShrink: 0, width: '100%', padding: '11px',
            border: '1px solid rgba(139,92,246,0.32)', borderRadius: 10,
            background: 'rgba(139,92,246,0.06)', color: '#a855f7',
            fontSize: 11, fontWeight: 700, letterSpacing: '0.08em',
            textTransform: 'uppercase', cursor: 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 7,
            transition: 'all 0.2s ease',
          }}
          onMouseEnter={e => { e.currentTarget.style.background = 'rgba(139,92,246,0.13)'; e.currentTarget.style.borderColor = 'rgba(139,92,246,0.55)' }}
          onMouseLeave={e => { e.currentTarget.style.background = 'rgba(139,92,246,0.06)'; e.currentTarget.style.borderColor = 'rgba(139,92,246,0.32)' }}>
            ◊&nbsp;Why was this refused?
          </button>
        )}

        {error && (
          <div style={{
            flexShrink: 0, color: 'var(--danger)', fontSize: 12,
            background: 'rgba(244,63,94,0.06)', border: '1px solid rgba(244,63,94,0.22)',
            borderRadius: 8, padding: '10px 14px',
          }}>{error}</div>
        )}
      </div>

      {/* ── RIGHT: Drop zones ── */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12, minHeight: 0 }}>
        <div style={{
          flex: 1, minHeight: 0,
          display: 'grid', gridTemplateColumns: '1fr auto 1fr', gap: 14, alignItems: 'stretch',
        }}>
          <DropZone label="First Subject"  slot="A" file={fileA} onFile={setFileA} />

          {/* VS separator */}
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 10 }}>
            <div style={{ width: 1, flex: 1, background: 'linear-gradient(to bottom, transparent, rgba(0,229,255,0.25), transparent)' }} />
            <div style={{ position: 'relative', width: 54, height: 54, flexShrink: 0 }}>
              <div style={{
                position: 'absolute', inset: 0, borderRadius: '50%',
                background: 'conic-gradient(from 0deg, var(--accent), #8b5cf6, var(--accent))',
                animation: 'spin 8s linear infinite', opacity: 0.5,
              }}/>
              <div style={{
                position: 'absolute', inset: 2, borderRadius: '50%',
                background: 'var(--bg-base)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 13, fontWeight: 900, letterSpacing: '0.04em', color: 'var(--accent)',
              }}>VS</div>
            </div>
            <div style={{ width: 1, flex: 1, background: 'linear-gradient(to bottom, rgba(0,229,255,0.25), transparent)' }} />
          </div>

          <DropZone label="Second Subject" slot="B" file={fileB} onFile={setFileB} />
        </div>

        <button className="btn-primary" onClick={handleVerify}
          disabled={loading || (!fileA && !fileB)}
          style={{ flexShrink: 0, width: '100%', padding: '16px', fontSize: 13, letterSpacing: '0.12em' }}>
          {loading
            ? <><span className="spin" style={{ marginRight: 8 }}>◌</span>Running ArcFace Inference…</>
            : '◈  Run Verification'
          }
        </button>
      </div>
    </div>

    {modalOpen && (
      <ExplainModal explanation={explanation} explaining={explaining} onClose={() => setModalOpen(false)} />
    )}
    </>
  )
}
