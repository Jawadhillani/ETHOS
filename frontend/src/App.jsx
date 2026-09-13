import { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import Nav from './components/Nav'
import StatusBar from './components/StatusBar'
import BackgroundFx from './components/BackgroundFx'
import Overview from './pages/Overview'
import Verify from './pages/Verify'
import Identify from './pages/Identify'
import Enroll from './pages/Enroll'
import Fairness from './pages/Fairness'
import Metrics from './pages/Metrics'
import EthicsChat from './pages/EthicsChat'
import LivePAD from './pages/LivePAD'
import Report from './pages/Report'

const PAGES = {
  overview: Overview,
  verify:   Verify,
  identify: Identify,
  enroll:   Enroll,
  fairness: Fairness,
  metrics:  Metrics,
  chat:     EthicsChat,
  pad:      LivePAD,
  report:   Report,
}

const variants = {
  initial: { opacity: 0, y: 22, filter: 'blur(4px)', scale: 0.99 },
  animate: { opacity: 1, y: 0, filter: 'blur(0px)', scale: 1, transition: { duration: 0.32, ease: [0.34, 1.18, 0.64, 1] } },
  exit:    { opacity: 0, y: -12, filter: 'blur(3px)', scale: 0.99, transition: { duration: 0.18, ease: [0.4, 0, 1, 1] } },
}

export default function App() {
  const [page, setPage] = useState('overview')
  const PageComponent = PAGES[page] ?? Overview

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', position: 'relative', zIndex: 1 }}>
      <BackgroundFx />
      <Nav current={page} onNav={setPage} />
      <div style={{ flex: 1, position: 'relative', zIndex: 1 }}>
        <AnimatePresence mode="wait">
          <motion.div key={page} {...variants}>
            <PageComponent onNav={setPage} />
          </motion.div>
        </AnimatePresence>
      </div>
      <StatusBar />
    </div>
  )
}
