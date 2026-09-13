import { useEffect, useRef } from 'react'

// Deterministic particle field — 30 floating glowing dots
const PARTICLES = [
  [4,  20, 2,   18, -2,  '#00e5ff', 0.22],
  [9,  70, 1.5, 22, -8,  '#8b5cf6', 0.16],
  [14, 40, 2.5, 16, -4,  '#00e5ff', 0.18],
  [18, 85, 1,   25, -11, '#f0abfc', 0.13],
  [23, 55, 2,   20, -6,  '#10b981', 0.17],
  [28, 15, 1.5, 17, -13, '#00e5ff', 0.20],
  [33, 75, 2,   23, -3,  '#8b5cf6', 0.15],
  [38, 45, 1,   19, -9,  '#00e5ff', 0.18],
  [42, 90, 2.5, 21, -5,  '#f0abfc', 0.14],
  [47, 30, 1.5, 15, -15, '#10b981', 0.19],
  [52, 65, 2,   24, -7,  '#00e5ff', 0.16],
  [57, 50, 1.5, 18, -10, '#8b5cf6', 0.14],
  [62, 80, 2,   22, -1,  '#00e5ff', 0.20],
  [67, 25, 1,   16, -14, '#f0abfc', 0.15],
  [72, 60, 2.5, 20, -6,  '#10b981', 0.17],
  [77, 10, 1.5, 26, -12, '#00e5ff', 0.21],
  [82, 75, 2,   17, -4,  '#8b5cf6', 0.13],
  [87, 35, 1.5, 21, -8,  '#00e5ff', 0.19],
  [92, 55, 2,   19, -16, '#f0abfc', 0.16],
  [97, 88, 1,   23, -3,  '#10b981', 0.12],
  [11, 45, 1.5, 20, -17, '#00e5ff', 0.17],
  [22, 82, 2,   18, -9,  '#8b5cf6', 0.20],
  [34, 18, 1,   24, -5,  '#f0abfc', 0.13],
  [46, 72, 2.5, 16, -11, '#00e5ff', 0.18],
  [58, 38, 1.5, 22, -7,  '#10b981', 0.16],
  [70, 92, 2,   17, -13, '#8b5cf6', 0.14],
  [83, 58, 1,   25, -2,  '#00e5ff', 0.15],
  [95, 28, 2,   20, -16, '#f0abfc', 0.18],
  [6,  62, 1.5, 19, -10, '#10b981', 0.14],
  [50, 8,  2,   23, -7,  '#00e5ff', 0.20],
]

export default function BackgroundFx() {
  const cursorRef = useRef(null)

  useEffect(() => {
    const move = e => {
      if (cursorRef.current) {
        cursorRef.current.style.transform =
          `translate(${e.clientX - 320}px, ${e.clientY - 320}px)`
      }
    }
    window.addEventListener('mousemove', move, { passive: true })
    return () => window.removeEventListener('mousemove', move)
  }, [])

  return (
    <div style={{ position: 'fixed', inset: 0, pointerEvents: 'none', zIndex: 0, overflow: 'hidden' }}>

      <style>{`
        @keyframes particle-rise {
          0%   { transform: translateY(0) scale(1); opacity: 1; }
          85%  { opacity: 1; }
          100% { transform: translateY(-100vh) scale(0.5); opacity: 0; }
        }
        @keyframes orb1 { from { transform: translate(0,0) scale(1); } to { transform: translate(100px,-80px) scale(1.18); } }
        @keyframes orb2 { from { transform: translate(0,0) scale(1); } to { transform: translate(-80px,100px) scale(0.85); } }
        @keyframes orb3 { from { transform: translate(0,0) scale(1); } to { transform: translate(70px,-90px) scale(1.14); } }
        @keyframes orb4 { from { transform: translate(0,0) scale(1); } to { transform: translate(-60px,80px) scale(0.8); } }
      `}</style>

      {/* GPU-accelerated cursor radial glow */}
      <div ref={cursorRef} style={{
        position: 'fixed', top: 0, left: 0,
        width: 640, height: 640, borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(0,229,255,0.055) 0%, rgba(139,92,246,0.02) 40%, transparent 70%)',
        willChange: 'transform',
        transition: 'transform 0.06s linear',
      }}/>

      {/* Floating particle field */}
      {PARTICLES.map(([x, startY, size, dur, delay, color, opacity], i) => (
        <div key={i} style={{
          position: 'absolute',
          left: `${x}%`,
          top: `${startY}%`,
          width: size, height: size,
          borderRadius: '50%',
          background: color,
          boxShadow: `0 0 ${size * 4}px ${color}, 0 0 ${size * 8}px ${color}55`,
          opacity,
          animation: `particle-rise ${dur}s linear ${delay}s infinite`,
          willChange: 'transform, opacity',
        }}/>
      ))}

      {/* Ambient orbs */}
      <div style={{ position: 'absolute', width: 900, height: 900, left: '-22%', top: '5%', borderRadius: '50%', background: 'radial-gradient(circle, rgba(0,229,255,0.09) 0%, transparent 60%)', animation: 'orb1 28s ease-in-out infinite alternate' }}/>
      <div style={{ position: 'absolute', width: 750, height: 750, right: '-16%', top: '-12%', borderRadius: '50%', background: 'radial-gradient(circle, rgba(139,92,246,0.11) 0%, transparent 60%)', animation: 'orb2 34s ease-in-out infinite alternate' }}/>
      <div style={{ position: 'absolute', width: 620, height: 620, right: '14%', bottom: '-16%', borderRadius: '50%', background: 'radial-gradient(circle, rgba(16,185,129,0.08) 0%, transparent 65%)', animation: 'orb3 22s ease-in-out infinite alternate' }}/>
      <div style={{ position: 'absolute', width: 480, height: 480, left: '38%', top: '32%', borderRadius: '50%', background: 'radial-gradient(circle, rgba(0,229,255,0.05) 0%, transparent 70%)', animation: 'orb4 40s ease-in-out infinite alternate' }}/>
      <div style={{ position: 'absolute', width: 560, height: 560, left: '52%', bottom: '12%', borderRadius: '50%', background: 'radial-gradient(circle, rgba(240,171,252,0.07) 0%, transparent 65%)', animation: 'orb3 48s ease-in-out infinite alternate-reverse' }}/>

      {/* Diagonal cinematic light beams */}
      <div style={{ position: 'absolute', top: -400, right: '6%', width: 3, height: '130vh', background: 'linear-gradient(180deg, transparent 0%, rgba(0,229,255,0.1) 25%, rgba(139,92,246,0.06) 65%, transparent 100%)', transform: 'rotate(-18deg)', transformOrigin: 'top center', filter: 'blur(16px)' }}/>
      <div style={{ position: 'absolute', top: -300, left: '12%', width: 2, height: '110vh', background: 'linear-gradient(180deg, transparent 0%, rgba(139,92,246,0.08) 35%, rgba(0,229,255,0.04) 75%, transparent 100%)', transform: 'rotate(14deg)', transformOrigin: 'top center', filter: 'blur(22px)' }}/>
      <div style={{ position: 'absolute', top: -200, right: '40%', width: 1, height: '90vh', background: 'linear-gradient(180deg, transparent 0%, rgba(240,171,252,0.07) 40%, transparent 100%)', transform: 'rotate(-5deg)', filter: 'blur(12px)' }}/>

      {/* Vignette */}
      <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at center, transparent 30%, rgba(6,12,24,0.75) 100%)' }}/>

      {/* Grain texture tile */}
      <div style={{
        position: 'absolute', inset: 0,
        backgroundImage: 'url("data:image/svg+xml,%3Csvg viewBox=\'0 0 512 512\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cfilter id=\'n\'%3E%3CfeTurbulence type=\'fractalNoise\' baseFrequency=\'0.75\' numOctaves=\'4\' stitchTiles=\'stitch\'/%3E%3C/filter%3E%3Crect width=\'512\' height=\'512\' filter=\'url(%23n)\' opacity=\'1\'/%3E%3C/svg%3E")',
        backgroundSize: '200px 200px',
        opacity: 0.04, mixBlendMode: 'screen',
      }}/>

      {/* Scan lines */}
      <div style={{ position: 'absolute', inset: 0, backgroundImage: 'repeating-linear-gradient(0deg, rgba(0,229,255,0.018) 0px, rgba(0,229,255,0.018) 1px, transparent 1px, transparent 100px)' }}/>
    </div>
  )
}
