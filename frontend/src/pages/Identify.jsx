import { useState, useEffect } from 'react'
import { identifyFace, explainResult } from '../api'

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
        width: '100%', maxWidth: 540,
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
            }}>◊</div>
            <div>
              <div style={{ fontSize: 12, fontWeight: 800, letterSpacing: '0.1em', textTransform: 'uppercase', color: '#a855f7' }}>
                Claude · Match Analysis
              </div>
              <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 2 }}>AI-generated explanation</div>
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
          onMouseLeave={e => { e.currentTarget.style.borderColor = 'rgba(255,255,255,0.1)'; e.currentTarget.style.color = 'var(--text-muted)' }}>✕</button>
        </div>

        <div style={{ padding: '28px 28px 32px' }}>
          {explaining ? (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16, padding: '20px 0' }}>
              <div style={{
                width: 36, height: 36, borderRadius: '50%',
                border: '2px solid rgba(139,92,246,0.2)', borderTopColor: '#a855f7',
                animation: 'spin 0.9s linear infinite',
              }}/>
              <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>Analysing matches…</span>
            </div>
          ) : (
            <p style={{ fontSize: 14, color: 'var(--text-sec)', lineHeight: 1.8, margin: 0 }}>
              {explanation}
            </p>
          )}
        </div>

        {!explaining && (
          <div style={{ padding: '14px 28px', borderTop: '1px solid rgba(139,92,246,0.1)', display: 'flex', justifyContent: 'flex-end' }}>
            <button onClick={onClose} className="btn-ghost" style={{ padding: '8px 24px', fontSize: 11 }}>Close</button>
          </div>
        )}
      </div>
    </div>
  )
}

const RACE_COLORS = {
  'White': '#00e5ff', 'Black': '#f59e0b', 'Latino_Hispanic': '#10b981',
  'East Asian': '#a78bfa', 'Southeast Asian': '#f472b6',
  'Indian': '#34d399', 'Middle Eastern': '#fbbf24',
}

function QueryZone({ file, onFile }) {
  const [drag, setDrag] = useState(false)
  const preview = file ? URL.createObjectURL(file) : null
  const borderColor = drag ? 'rgba(0,229,255,0.6)' : file ? 'rgba(0,229,255,0.28)' : 'rgba(255,255,255,0.08)'

  return (
    <label style={{
      display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
      gap: 16, cursor: 'pointer', borderRadius: 16, minHeight: 300,
      background: drag ? 'rgba(0,229,255,0.04)' : 'rgba(16,25,50,0.7)',
      border: `1px solid ${borderColor}`,
      boxShadow: drag
        ? '0 0 60px rgba(0,229,255,0.12), inset 0 0 40px rgba(0,229,255,0.04)'
        : file ? '0 0 30px rgba(0,229,255,0.05)' : 'none',
      position: 'relative', overflow: 'hidden',
      transition: 'all 0.25s ease',
    }}
    onDragOver={e => { e.preventDefault(); setDrag(true) }}
    onDragLeave={() => setDrag(false)}
    onDrop={e => {
      e.preventDefault(); setDrag(false)
      const f = e.dataTransfer.files[0]
      if (f?.type.startsWith('image/')) onFile(f)
    }}>
      <input type="file" accept="image/*" style={{ display: 'none' }}
        onChange={e => e.target.files[0] && onFile(e.target.files[0])} />

      {[['top','left'], ['top','right'], ['bottom','left'], ['bottom','right']].map(([v, h]) => (
        <div key={`${v}${h}`} style={{
          position: 'absolute', [v]: 12, [h]: 12, width: 18, height: 18,
          borderTop: v === 'top' ? `2px solid rgba(0,229,255,${file ? 0.5 : 0.22})` : 'none',
          borderBottom: v === 'bottom' ? `2px solid rgba(0,229,255,${file ? 0.5 : 0.22})` : 'none',
          borderLeft: h === 'left' ? `2px solid rgba(0,229,255,${file ? 0.5 : 0.22})` : 'none',
          borderRight: h === 'right' ? `2px solid rgba(0,229,255,${file ? 0.5 : 0.22})` : 'none',
        }} />
      ))}

      <div style={{
        position: 'absolute', top: 14, left: '50%', transform: 'translateX(-50%)',
        fontSize: 9, fontWeight: 800, letterSpacing: '0.18em', textTransform: 'uppercase',
        color: file ? 'var(--accent)' : 'var(--text-muted)',
        background: 'rgba(12,20,42,0.8)', backdropFilter: 'blur(6px)',
        border: `1px solid ${file ? 'rgba(0,229,255,0.2)' : 'rgba(255,255,255,0.06)'}`,
        borderRadius: 6, padding: '3px 10px', whiteSpace: 'nowrap',
      }}>Query Image</div>

      {preview ? (
        <img src={preview} alt="query" style={{
          maxWidth: '85%', maxHeight: 230, borderRadius: 12,
          objectFit: 'contain', boxShadow: '0 10px 40px rgba(0,0,0,0.7)',
        }} />
      ) : (
        <div style={{ textAlign: 'center', padding: '20px 0' }}>
          <div style={{
            width: 64, height: 64, borderRadius: 20,
            border: '1px solid rgba(0,229,255,0.14)',
            background: 'rgba(0,229,255,0.025)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 16px', fontSize: 26, color: 'rgba(0,229,255,0.25)',
          }}>⊕</div>
          <div style={{ fontSize: 14, color: 'var(--text-muted)', fontWeight: 500, lineHeight: 1.6 }}>
            <span style={{ color: 'var(--accent)', fontWeight: 700 }}>Click to upload</span>
            <br /><span style={{ fontSize: 12 }}>query face photo</span>
          </div>
        </div>
      )}
    </label>
  )
}

export default function Identify() {
  const [file, setFile] = useState(null)
  const [topK, setTopK] = useState(5)
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [modalOpen, setModalOpen] = useState(false)
  const [explanation, setExplanation] = useState(null)
  const [explaining, setExplaining] = useState(false)

  async function handleIdentify() {
    if (!file) { setError('Upload an image first.'); return }
    setLoading(true); setError(''); setResults(null); setExplanation(null); setModalOpen(false)
    try { setResults(await identifyFace(file, topK)) }
    catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  async function handleExplain() {
    setModalOpen(true); setExplaining(true); setExplanation(null)
    try {
      const res = await explainResult('identify', { results: results.results, n_gallery: results.n_gallery })
      setExplanation(res.explanation)
    } catch (e) { setExplanation('Could not generate explanation: ' + e.message) }
    finally { setExplaining(false) }
  }

  return (
    <>
    <div style={{ maxWidth: 1060, margin: '0 auto', padding: '48px 28px 60px' }}>
      <div style={{ marginBottom: 40 }}>
        <div className="page-eyebrow">
          <span style={{
            display: 'inline-block', width: 5, height: 5, borderRadius: '50%',
            background: 'var(--accent)', animation: 'dot-pulse 2s ease-in-out infinite',
          }}/>
          1 : N Identification
        </div>
        <h2 style={{
          fontSize: 40, fontWeight: 900, letterSpacing: '-0.03em',
          background: 'linear-gradient(135deg, var(--text-pri) 0%, var(--accent) 100%)',
          WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text',
          marginBottom: 10,
        }}>Face Identification</h2>
        <p className="section-sub" style={{ fontSize: 16 }}>
          Search the FairFace 86k gallery · ArcFace embeddings · cosine nearest-neighbor
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: 28, alignItems: 'start' }}>
        {/* Left panel */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <QueryZone file={file} onFile={setFile} />

          <div className="card-glow">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
              <span style={{ fontSize: 10, fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                Top-K Results
              </span>
              <span style={{
                fontSize: 26, fontWeight: 900, color: 'var(--accent)',
                fontFamily: "'Orbitron',sans-serif",
                textShadow: '0 0 16px rgba(0,229,255,0.6)',
              }}>{topK}</span>
            </div>
            <input type="range" min={1} max={10} step={1} value={topK}
              onChange={e => setTopK(parseInt(e.target.value))}
              style={{ width: '100%', accentColor: 'var(--accent)', cursor: 'pointer' }} />
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 6,
              fontSize: 9, color: 'var(--text-muted)', fontWeight: 600 }}>
              <span>1</span><span>10</span>
            </div>
          </div>

          <button className="btn-primary" onClick={handleIdentify} disabled={loading || !file}
            style={{ width: '100%', padding: '14px', fontSize: 12, letterSpacing: '0.1em' }}>
            {loading
              ? <><span className="spin" style={{ marginRight: 8 }}>◌</span>Searching gallery…</>
              : '⊕  Search Gallery'
            }
          </button>

          {error && (
            <div style={{
              color: 'var(--danger)', fontSize: 13,
              background: 'rgba(244,63,94,0.06)', border: '1px solid rgba(244,63,94,0.22)',
              borderRadius: 8, padding: '10px 14px',
            }}>{error}</div>
          )}

          {results && (
            <>
              <div style={{
                fontSize: 12, color: 'var(--text-sec)',
                background: 'linear-gradient(135deg, rgba(0,229,255,0.03), rgba(0,229,255,0.01))',
                border: '1px solid rgba(0,229,255,0.08)',
                borderRadius: 10, padding: '11px 14px', lineHeight: 1.8,
              }}>
                <div>Gallery: <b style={{ color: 'var(--text-pri)' }}>{results.n_gallery?.toLocaleString()}</b> images</div>
                <div>Returned: <b style={{ color: 'var(--accent)' }}>{results.results?.length ?? 0}</b> matches</div>
              </div>

              <button onClick={handleExplain} style={{
                width: '100%', padding: '11px',
                border: '1px solid rgba(139,92,246,0.32)',
                borderRadius: 10, background: 'rgba(139,92,246,0.06)',
                color: '#a855f7', fontSize: 11, fontWeight: 700,
                letterSpacing: '0.08em', textTransform: 'uppercase', cursor: 'pointer',
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 7,
                transition: 'all 0.2s ease',
              }}
              onMouseEnter={e => { e.currentTarget.style.background = 'rgba(139,92,246,0.13)'; e.currentTarget.style.borderColor = 'rgba(139,92,246,0.55)' }}
              onMouseLeave={e => { e.currentTarget.style.background = 'rgba(139,92,246,0.06)'; e.currentTarget.style.borderColor = 'rgba(139,92,246,0.32)' }}>
                ◊&nbsp;AI Analysis
              </button>
            </>
          )}
        </div>

        {/* Right panel: results */}
        <div>
          {!results && !loading && (
            <div style={{
              display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
              height: 340,
              border: '1px dashed rgba(255,255,255,0.07)', borderRadius: 18,
              color: 'var(--text-muted)', gap: 18,
            }}>
              <div style={{
                width: 70, height: 70, borderRadius: '50%',
                border: '1px solid rgba(0,229,255,0.1)',
                background: 'rgba(0,229,255,0.02)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 30, color: 'rgba(0,229,255,0.18)',
              }}>⊕</div>
              <div style={{ fontSize: 14, fontWeight: 500 }}>Upload a face and click Search Gallery</div>
            </div>
          )}

          {loading && (
            <div style={{
              display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
              height: 340, gap: 22,
            }}>
              <div style={{
                position: 'relative', width: 70, height: 70,
              }}>
                <div style={{
                  position: 'absolute', inset: 0, borderRadius: '50%',
                  border: '2px solid rgba(0,229,255,0.1)',
                  borderTopColor: 'var(--accent)',
                  animation: 'spin 0.85s linear infinite',
                }}/>
                <div style={{
                  position: 'absolute', inset: 10, borderRadius: '50%',
                  border: '2px solid rgba(139,92,246,0.1)',
                  borderTopColor: '#a855f7',
                  animation: 'spin 1.4s linear infinite reverse',
                }}/>
              </div>
              <div style={{ color: 'var(--accent)', fontSize: 13, fontWeight: 700, letterSpacing: '0.08em' }}>
                Searching 86k gallery…
              </div>
            </div>
          )}

          {results?.results && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {/* Header */}
              <div style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '0 20px 0 64px', marginBottom: 2,
                fontSize: 9, fontWeight: 800, letterSpacing: '0.14em', textTransform: 'uppercase',
                color: 'var(--text-muted)',
              }}>
                <span style={{ flex: 1 }}>Identity Match</span>
                <span style={{ width: 210, textAlign: 'center' }}>Biometric Profile</span>
                <span style={{ width: 100, textAlign: 'right' }}>Similarity</span>
              </div>

              {results.results.map((r, i) => {
                const isTop = i === 0
                const rc = RACE_COLORS[r.race] ?? '#8aafd4'
                const maxSim = results.results[0]?.similarity ?? 1
                // Normalize bar relative to top match so differences are visible
                const barPct = Math.round((r.similarity / maxSim) * 100)
                const rawPct = Math.round(r.similarity * 100)

                return (
                  <div key={i} style={{
                    display: 'flex', alignItems: 'center', gap: 0,
                    position: 'relative',
                    background: isTop
                      ? `linear-gradient(135deg, ${rc}10 0%, rgba(12,20,44,0.98) 55%)`
                      : 'linear-gradient(145deg, rgba(15,24,50,0.92), rgba(10,18,40,0.97))',
                    border: `1px solid ${isTop ? `${rc}44` : 'rgba(255,255,255,0.05)'}`,
                    borderLeft: `4px solid ${rc}${isTop ? 'ff' : '88'}`,
                    borderRadius: 16,
                    boxShadow: isTop ? `0 6px 48px ${rc}1a, inset 0 1px 0 rgba(255,255,255,0.04)` : 'none',
                    transition: 'transform 0.22s ease, box-shadow 0.22s ease',
                    cursor: 'default',
                    overflow: 'hidden',
                    animation: `card-in 0.45s cubic-bezier(0.34,1.3,0.64,1) ${i * 0.08}s both`,
                  }}
                  onMouseEnter={e => {
                    e.currentTarget.style.transform = 'translateX(6px)'
                    e.currentTarget.style.boxShadow = `0 10px 52px ${rc}28`
                  }}
                  onMouseLeave={e => {
                    e.currentTarget.style.transform = ''
                    e.currentTarget.style.boxShadow = isTop ? `0 6px 48px ${rc}1a` : 'none'
                  }}>

                    {/* Rank badge */}
                    <div style={{
                      width: 60, flexShrink: 0,
                      display: 'flex', justifyContent: 'center', padding: '18px 0',
                    }}>
                      <div style={{
                        width: 40, height: 40, borderRadius: 12,
                        background: `${rc}1a`,
                        border: `1.5px solid ${rc}60`,
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: isTop ? 15 : 13, fontWeight: 900,
                        color: rc, fontFamily: "'Orbitron',sans-serif",
                        textShadow: `0 0 16px ${rc}dd`,
                        boxShadow: isTop ? `0 0 24px ${rc}44` : 'none',
                      }}>{r.rank}</div>
                    </div>

                    {/* Identity: filename + normalized similarity bar */}
                    <div style={{ flex: 1, minWidth: 0, padding: '18px 20px 18px 0' }}>
                      <div style={{
                        fontSize: isTop ? 14 : 13,
                        color: isTop ? '#f0f6ff' : 'rgba(170,200,240,0.75)',
                        fontWeight: isTop ? 700 : 500,
                        overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                        marginBottom: 10,
                        letterSpacing: '0.01em',
                      }}>{r.filename}</div>

                      {/* Bar + raw % */}
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <div style={{
                          flex: 1, height: 5, background: 'rgba(255,255,255,0.05)',
                          borderRadius: 3, overflow: 'hidden',
                        }}>
                          <div style={{
                            width: `${barPct}%`, height: '100%',
                            background: `linear-gradient(90deg, ${rc}dd, ${rc}66)`,
                            borderRadius: 3,
                            boxShadow: `0 0 12px ${rc}66`,
                            transition: 'width 0.8s cubic-bezier(0.4,0,0.2,1) 0.1s',
                          }}/>
                        </div>
                        <span style={{
                          fontSize: 9.5, color: rc, fontWeight: 700,
                          fontFamily: 'monospace', opacity: 0.75, whiteSpace: 'nowrap',
                        }}>{rawPct}%</span>
                      </div>
                    </div>

                    {/* Biometric Profile — the hero section */}
                    <div style={{
                      width: 210, flexShrink: 0,
                      display: 'flex', flexDirection: 'column', gap: 8,
                      padding: '16px 20px',
                      borderLeft: '1px solid rgba(255,255,255,0.04)',
                    }}>
                      {/* Race — headline demographic */}
                      <div style={{
                        display: 'flex', alignItems: 'center', gap: 8,
                        background: `${rc}1c`,
                        border: `1.5px solid ${rc}70`,
                        borderRadius: 10,
                        padding: '7px 14px',
                        boxShadow: `0 0 20px ${rc}22`,
                      }}>
                        <span style={{
                          width: 8, height: 8, borderRadius: '50%',
                          background: rc, boxShadow: `0 0 10px ${rc}, 0 0 20px ${rc}88`,
                          display: 'inline-block', flexShrink: 0,
                          animation: isTop ? 'dot-pulse 2s ease-in-out infinite' : undefined,
                        }}/>
                        <span style={{
                          fontSize: 13, fontWeight: 800, color: rc,
                          letterSpacing: '0.03em',
                        }}>{r.race.replace(/_/g, ' ')}</span>
                        <span style={{
                          marginLeft: 'auto', fontSize: 8, fontWeight: 700,
                          color: `${rc}99`, letterSpacing: '0.1em', textTransform: 'uppercase',
                        }}>Race</span>
                      </div>

                      {/* Gender */}
                      <div style={{
                        display: 'flex', alignItems: 'center', gap: 7,
                        padding: '4px 12px',
                        background: 'rgba(255,255,255,0.03)',
                        border: '1px solid rgba(255,255,255,0.07)',
                        borderRadius: 8,
                      }}>
                        <span style={{
                          fontSize: 12,
                          color: r.gender === 'Male' ? '#60a5fa' : '#f472b6',
                        }}>
                          {r.gender === 'Male' ? '♂' : '♀'}
                        </span>
                        <span style={{
                          fontSize: 11, fontWeight: 600, letterSpacing: '0.05em',
                          color: 'rgba(180,210,240,0.7)',
                        }}>{r.gender}</span>
                        {r.age && (
                          <span style={{
                            marginLeft: 'auto', fontSize: 9, color: 'var(--text-muted)',
                            fontWeight: 500,
                          }}>{r.age}</span>
                        )}
                      </div>
                    </div>

                    {/* Similarity score */}
                    <div style={{
                      width: 100, flexShrink: 0,
                      display: 'flex', flexDirection: 'column', alignItems: 'flex-end',
                      justifyContent: 'center', padding: '0 22px',
                      borderLeft: '1px solid rgba(255,255,255,0.04)',
                    }}>
                      <div style={{
                        fontSize: isTop ? 20 : 16, fontWeight: 900,
                        color: isTop ? rc : 'rgba(160,190,230,0.7)',
                        fontFamily: "'Orbitron',sans-serif",
                        letterSpacing: '-0.02em',
                        textShadow: isTop ? `0 0 22px ${rc}cc` : 'none',
                        lineHeight: 1,
                      }}>{r.similarity.toFixed(4)}</div>
                      {isTop && (
                        <div style={{
                          fontSize: 7.5, fontWeight: 800, letterSpacing: '0.12em',
                          color: rc, opacity: 0.65, textTransform: 'uppercase',
                          marginTop: 5,
                        }}>Top Match</div>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </div>

    {modalOpen && (
      <ExplainModal explanation={explanation} explaining={explaining} onClose={() => setModalOpen(false)} />
    )}
    </>
  )
}
