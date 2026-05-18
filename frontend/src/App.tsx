import { useState } from 'react'
import { motion } from 'framer-motion'
import NatureBackground from './components/NatureBackground'
import BotVideo from './components/BotVideo'
import ChatWidget from './components/ChatWidget'
import logo from './video/logo.png'

export type BotState = 'idle' | 'thinking' | 'listening' | 'speaking'

const stateConfig: Record<BotState, { label: string; icon: string; hex: string; bg: string }> = {
  idle:      { label: 'Jim turishi', icon: '😶', hex: '#6b7280', bg: 'rgba(107,114,128,0.2)' },
  thinking:  { label: "O'ylayapti",  icon: '💭', hex: '#f59e0b', bg: 'rgba(245,158,11,0.2)' },
  listening: { label: 'Tinglayapti', icon: '🎤', hex: '#10b981', bg: 'rgba(16,185,129,0.2)' },
  speaking:  { label: 'Gapirmoqda', icon: '🔊', hex: '#3b82f6', bg: 'rgba(59,130,246,0.2)'  },
}

const videoMap: Record<BotState, string> = {
  idle:      '/idle.mp4',
  thinking:  '/thinking.mp4',
  listening: '/listening.mp4',
  speaking:  '/speaking.mp4',
}

export default function App() {
  const [botState, setBotState] = useState<BotState>('idle')

  return (
    <div className="relative w-full h-screen h-dvh overflow-hidden">
      <NatureBackground />

      {/* Bot videos — all mounted, crossfade between them */}
      {(Object.entries(videoMap) as [BotState, string][]).map(([state, src]) => (
        <motion.div
          key={state}
          animate={{ opacity: botState === state ? 1 : 0 }}
          transition={{ duration: 0.4 }}
          className="absolute bottom-0 left-1/2 -translate-x-1/2"
          style={{ pointerEvents: 'none' }}
        >
          <BotVideo src={src} className="w-[118rem] max-w-[95vw] sm:max-w-[85vw]" />
        </motion.div>
      ))}

      {/* Top-left: logo + title */}
      <div className="absolute top-4 left-4 sm:top-6 sm:left-6 flex items-center gap-2 sm:gap-3">
        <img src={logo} alt="logo" className="h-[44px] sm:h-[67px] w-auto drop-shadow-lg" />
        <div>
          <p className="text-white font-bold text-sm sm:text-lg leading-tight drop-shadow">
            Davlat Ekologik
          </p>
          <p className="text-white font-bold text-sm sm:text-lg leading-tight drop-shadow">
            Ekspertizasi Markazi
          </p>
        </div>
      </div>

      {/* Chat widget — mic, drawer, ticker */}
      <ChatWidget setBotState={setBotState} />
    </div>
  )
}
