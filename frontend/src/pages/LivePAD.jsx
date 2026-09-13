import { useEffect, useRef, useState, useCallback } from 'react'
import { processLivenessFrame } from '../api'

function ScoreGauge({ score, color }) {
  const R = 46, cx = 60, cy = 60
  const totalArc = 270
  const startAngle = 225
  const pct = score !== null ? Math.min(score, 1) : 0
  const fillDeg = pct * totalArc

  function arc(startDeg, endDeg, r) {
    const toRad = d => (d - 90) * Math.PI / 180
    const s = { x: cx + r * Math.cos(toRad(startDeg)), y: cy + r * Math.sin(toRad(startDeg)) }
    const e = { x: cx + r * Math.cos(toRad(endDeg)), y: cy + r * Math.sin(toRad(endDeg)) }
    const large = endDeg - startDeg > 180 ? 1 : 0
    return `M ${s.x} ${s.y} A ${r} ${r} 0 ${large} 1 ${e.x} ${e.y}`
  }

  return (
    <svg width={120} height={120} viewBox="0 0 120 120">
      <path d={arc(startAngle, startAngle + totalArc, R)} fill="none"
        stroke="rgba(255,255,255,0.06)" strokeWidth={10} strokeLinecap="round" />
      {fillDeg > 2 && (
        <path d={arc(startAngle, startAngle + fillDeg, R)} fill="none"
          stroke={color} strokeWidth={10} strokeLinecap="round"
          style={{ transition: 'stroke-dasharray 0.15s ease', filter: `drop-shadow(0 0 8px ${color}88)` }} />
      )}
      <text x={cx} y={cy + 2} textAnchor="middle" dominantBaseline="middle"
        fill={score !== null ? color : 'var(--text-muted)'}
        fontSize={score !== null ? 16 : 12} fontWeight={900}
        fontFamily="'Orbitron',Inter,sans-serif">
        {score !== null ? score.toFixed(3) : '—'}
      </text>
    </svg>
  )
}

export default function LivePAD() {
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const streamRef = useRef(null)
  const timerRef = useRef(null)
  const [active, setActive] = useState(false)
  const [fps, setFps] = useState(0)
  const [infMs, setInfMs] = useState(0)
  const [score, setScore] = useState(null)
  const [verdict, setVerdict] = useState(null)
  const [attackLabel, setAttackLabel] = useState('')
  const fpsTimesRef = useRef([])

  const startWebcam = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480, frameRate: 30 } })
      streamRef.current = stream
      if (videoRef.current) { videoRef.current.srcObject = stream; videoRef.current.play() }
      setActive(true)
    } catch (e) {
      alert('Camera access denied: ' + e.message)
    }
  }, [])

  const stopWebcam = useCallback(() => {
    clearInterval(timerRef.current)
    streamRef.current?.getTracks().forEach(t => t.stop())
    streamRef.current = null
    if (videoRef.current) videoRef.current.srcObject = null
    setActive(false); setFps(0); setScore(null); setVerdict(null)
  }, [])

  useEffect(() => {
    if (!active) return
    timerRef.current = setInterval(async () => {
      const video = videoRef.current
      const canvas = canvasRef.current
      if (!video || !canvas || video.readyState < 2) return
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      canvas.getContext('2d').drawImage(video, 0, 0)
      const b64 = canvas.toDataURL('image/jpeg', 0.7).split(',')[1]
      const now = performance.now() / 1000
      fpsTimesRef.current = [...fpsTimesRef.current.filter(t => now - t <= 2), now]
      const times = fpsTimesRef.current
      if (times.length > 1) setFps((times.length - 1) / (times[times.length - 1] - times[0]))
      const res = await processLivenessFrame(b64)
      if (res) {
        setScore(res.real_score); setAttackLabel(res.attack_label || '')
        setVerdict(res.is_real === null ? null : res.is_real ? 'real' : 'spoof')
        setInfMs(res.inference_ms || 0)
      }
    }, 40)
    return () => clearInterval(timerRef.current)
  }, [active])

  useEffect(() => () => stopWebcam(), [])

  const scoreColor = score === null ? 'var(--text-muted)'
    : score >= 0.75 ? 'var(--success)'
    : score >= 0.45 ? 'var(--warning)'
    : 'var(--danger)'

  const scoreLabel = score === null ? '—'
    : score >= 0.75 ? 'Real Face'
    : score >= 0.45 ? 'Uncertain'
    : 'Spoof Attack'

  const videoBorder = verdict === 'real'  ? 'rgba(16,185,129,0.45)'
                    : verdict === 'spoof' ? 'rgba(244,63,94,0.45)'
                    : 'rgba(255,255,255,0.08)'
  const videoGlow   = verdict === 'real'  ? '0 0 60px rgba(16,185,129,0.12)'
                    : verdict === 'spoof' ? '0 0 60px rgba(244,63,94,0.12)'
                    : 'none'

  return (
    <div style={{ maxWidth: 1060, margin: '0 auto', padding: '48px 28px 60px' }}>
      {/* Header */}
      <div style={{ marginBottom: 40 }}>
        <div className="page-eyebrow" style={{ animationName: 'badge-glow' }}>
          {active && (
            <span style={{
              display: 'inline-block', width: 6, height: 6, borderRadius: '50%',
              background: 'var(--danger)', animation: 'dot-pulse 1s ease-in-out infinite',
              boxShadow: '0 0 8px var(--danger)',
            }}/>
          )}
          {active ? 'LIVE · MiniFASNetV2' : 'Presentation Attack Detection'}
        </div>
        <h2 style={{
          fontSize: 40, fontWeight: 900, letterSpacing: '-0.03em',
          background: 'linear-gradient(135deg, var(--text-pri) 0%, var(--accent) 100%)',
          WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text',
          marginBottom: 8,
        }}>Live Liveness</h2>
        <p className="section-sub" style={{ fontSize: 16 }}>
          Real-time PAD via webcam · RetinaFace detection · MiniFASNetV2 · ≥10 FPS on M4
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 360px', gap: 24, alignItems: 'start' }}>
        {/* Video feed */}
        <div style={{ position: 'relative' }}>
          <div style={{
            borderRadius: 18, overflow: 'hidden',
            background: '#000',
            border: `1px solid ${videoBorder}`,
            aspectRatio: '4/3',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            position: 'relative',
            boxShadow: videoGlow,
            transition: 'border-color 0.3s ease, box-shadow 0.3s ease',
          }}>
            <video ref={videoRef} style={{ width: '100%', display: active ? 'block' : 'none', objectFit: 'cover' }} muted playsInline />

            {!active && (
              <div style={{ textAlign: 'center', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 18 }}>
                <div style={{
                  width: 80, height: 80, borderRadius: 24,
                  border: '1px solid rgba(0,229,255,0.1)',
                  background: 'rgba(0,229,255,0.02)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: 34, color: 'rgba(0,229,255,0.18)',
                }}>⊙</div>
                <div>
                  <div style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-sec)', marginBottom: 4 }}>Camera is off</div>
                  <div style={{ fontSize: 13 }}>Click Start Camera below</div>
                </div>
              </div>
            )}

            {/* Corner brackets */}
            {active && [['top', 'left'], ['top', 'right'], ['bottom', 'left'], ['bottom', 'right']].map(([v, h]) => (
              <div key={`${v}${h}`} style={{
                position: 'absolute', [v]: 14, [h]: 14, width: 22, height: 22,
                borderTop: v === 'top' ? `2px solid ${scoreColor}` : 'none',
                borderBottom: v === 'bottom' ? `2px solid ${scoreColor}` : 'none',
                borderLeft: h === 'left' ? `2px solid ${scoreColor}` : 'none',
                borderRight: h === 'right' ? `2px solid ${scoreColor}` : 'none',
                transition: 'border-color 0.3s ease',
              }} />
            ))}

            {/* FPS badge */}
            {active && (
              <div style={{
                position: 'absolute', top: 14, left: 14,
                background: 'rgba(10,18,38,0.88)', backdropFilter: 'blur(8px)',
                border: `1px solid ${fps >= 10 ? 'rgba(16,185,129,0.3)' : 'rgba(244,63,94,0.3)'}`,
                borderRadius: 8, padding: '5px 12px', fontSize: 11,
                display: 'flex', gap: 10, alignItems: 'center', fontFamily: 'monospace',
              }}>
                <span style={{ color: fps >= 10 ? 'var(--success)' : 'var(--danger)', fontWeight: 700 }}>
                  {fps.toFixed(1)} FPS
                </span>
                <span style={{ color: 'var(--text-muted)', fontSize: 9 }}>|</span>
                <span style={{ color: 'var(--text-muted)' }}>{infMs.toFixed(0)}ms</span>
              </div>
            )}

            {/* Verdict overlay */}
            {active && verdict && (
              <div style={{
                position: 'absolute', bottom: 14, left: '50%', transform: 'translateX(-50%)',
                background: verdict === 'real' ? 'rgba(16,185,129,0.88)' : 'rgba(244,63,94,0.88)',
                backdropFilter: 'blur(8px)',
                borderRadius: 10, padding: '7px 22px',
                fontSize: 13, fontWeight: 800, letterSpacing: '0.1em', textTransform: 'uppercase',
                color: '#fff', whiteSpace: 'nowrap',
                boxShadow: verdict === 'real' ? '0 0 24px rgba(16,185,129,0.4)' : '0 0 24px rgba(244,63,94,0.4)',
              }}>
                {verdict === 'real' ? '✓ Real Face' : `✗ Spoof${attackLabel ? ' · ' + attackLabel : ''}`}
              </div>
            )}
          </div>
          <canvas ref={canvasRef} style={{ display: 'none' }} />
        </div>

        {/* Right controls */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {/* Start/Stop */}
          <button onClick={active ? stopWebcam : startWebcam} style={{
            width: '100%', padding: '16px',
            fontSize: 12, fontWeight: 800, letterSpacing: '0.1em',
            textTransform: 'uppercase', border: 'none', cursor: 'pointer',
            borderRadius: 12, transition: 'all 0.22s ease',
            background: active
              ? 'rgba(244,63,94,0.08)'
              : 'linear-gradient(135deg, var(--accent), #0099cc)',
            color: active ? 'var(--danger)' : '#020710',
            border: active ? '1px solid rgba(244,63,94,0.32)' : 'none',
            boxShadow: active ? 'none' : '0 0 36px rgba(0,229,255,0.35)',
          }}>
            {active ? '■  Stop Camera' : '▶  Start Camera'}
          </button>

          {/* Gauge + score */}
          <div className="card-glow" style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 9, fontWeight: 800, letterSpacing: '0.16em', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: 12 }}>
              Liveness Score
            </div>
            <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 8 }}>
              <ScoreGauge score={score} color={scoreColor} />
            </div>
            <div style={{ fontSize: 11, fontWeight: 800, letterSpacing: '0.08em', textTransform: 'uppercase', color: scoreColor }}>
              {scoreLabel}
            </div>
          </div>

          {/* Verdict card */}
          <div style={{
            padding: '24px', borderRadius: 14,
            background: verdict === 'real'  ? 'rgba(16,185,129,0.06)'
                      : verdict === 'spoof' ? 'rgba(244,63,94,0.06)'
                      : 'linear-gradient(145deg, rgba(22,34,62,0.7), rgba(14,22,46,0.65))',
            border: verdict === 'real'  ? '1px solid rgba(16,185,129,0.3)'
                  : verdict === 'spoof' ? '1px solid rgba(244,63,94,0.3)'
                  : '1px solid rgba(255,255,255,0.06)',
            textAlign: 'center', transition: 'all 0.3s ease',
            boxShadow: verdict === 'real'  ? '0 0 48px rgba(16,185,129,0.08)'
                     : verdict === 'spoof' ? '0 0 48px rgba(244,63,94,0.08)' : 'none',
            minHeight: 110, display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            {!verdict && (
              <div style={{ color: 'var(--text-muted)', fontSize: 13 }}>
                {active ? 'Waiting for face…' : 'Camera off'}
              </div>
            )}
            {verdict === 'real' && (
              <div>
                <div style={{
                  fontSize: 44, fontWeight: 900, color: 'var(--success)',
                  fontFamily: "'Orbitron',sans-serif", letterSpacing: '0.05em', lineHeight: 1,
                  textShadow: '0 0 32px rgba(16,185,129,0.5)',
                  animation: 'verdict-in 0.3s ease both',
                }}>REAL</div>
                <div style={{ fontSize: 12, color: 'var(--success)', marginTop: 8, opacity: 0.7 }}>
                  Face confirmed live
                </div>
              </div>
            )}
            {verdict === 'spoof' && (
              <div>
                <div style={{
                  fontSize: 44, fontWeight: 900, color: 'var(--danger)',
                  fontFamily: "'Orbitron',sans-serif", letterSpacing: '0.05em', lineHeight: 1,
                  textShadow: '0 0 32px rgba(244,63,94,0.5)',
                  animation: 'verdict-in 0.3s ease both',
                }}>SPOOF</div>
                {attackLabel && (
                  <div style={{ fontSize: 12, color: 'var(--danger)', marginTop: 8, opacity: 0.7 }}>
                    {attackLabel}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Spec info */}
          <div style={{
            background: 'linear-gradient(145deg, rgba(20,30,56,0.8), rgba(14,22,46,0.85))',
            border: '1px solid rgba(255,255,255,0.06)',
            borderRadius: 12, padding: '18px',
          }}>
            {[
              ['Model',    'MiniFASNetV2'],
              ['Detector', 'RetinaFace'],
              ['Runtime',  'CoreML · Apple M4'],
              ['Target',   '≥10 FPS'],
              ['Threshold','0.75 (real face)'],
            ].map(([k, v]) => (
              <div key={k} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 9 }}>
                <span style={{ fontSize: 10, color: 'var(--text-muted)', fontWeight: 600, letterSpacing: '0.04em' }}>{k}</span>
                <span style={{ fontSize: 10, color: 'var(--text-sec)', fontWeight: 700, letterSpacing: '0.04em' }}>{v}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
