import { useState } from 'react'
import { motion } from 'framer-motion'
import NatureBackground from './components/NatureBackground'
import BotVideo from './components/BotVideo'
import thinkingVideo from './video/thinking.mp4'
import speakingVideo from './video/speaking.mp4'
import logo from './video/logo.png'

export type BotState = 'idle' | 'thinking' | 'listening' | 'speaking'

const stateConfig: Record<BotState, { label: string; icon: string; hex: string; bg: string }> = {
  idle:      { label: 'Jim turishi', icon: '😶', hex: '#6b7280', bg: 'rgba(107,114,128,0.2)' },
  thinking:  { label: "O'ylayapti",  icon: '💭', hex: '#f59e0b', bg: 'rgba(245,158,11,0.2)' },
  listening: { label: 'Tinglayapti', icon: '🎤', hex: '#10b981', bg: 'rgba(16,185,129,0.2)' },
  speaking:  { label: 'Gapirmoqda', icon: '🔊', hex: '#3b82f6', bg: 'rgba(59,130,246,0.2)'  },
}

// Videos ready so far; idle & listening will be added later
const videoMap: Partial<Record<BotState, string>> = {
  thinking: thinkingVideo,
  speaking: speakingVideo,
}

// Buttons shown until all 4 videos are ready
const visibleButtons: BotState[] = ['thinking', 'speaking']

export default function App() {
  const [botState, setBotState] = useState<BotState>('thinking')

  return (
    <div className="relative w-full h-screen overflow-hidden">
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
          <BotVideo src={src} className="w-[118rem] max-w-[95vw]" />
        </motion.div>
      ))}

      {/* Top-left: logo + title */}
      <div className="absolute top-6 left-6 flex items-center gap-3">
        <img src={logo} alt="logo" className="h-[67px] w-auto drop-shadow-lg" />
        <div>
          <p className="text-white font-bold text-lg leading-tight drop-shadow">
            Davlat Ekologik
          </p>
          <p className="text-white font-bold text-lg leading-tight drop-shadow">
            Ekspertizasi Markazi
          </p>
        </div>
      </div>

      {/* Top-right: thinking + speaking buttons only */}
      <div className="absolute top-8 right-8 flex flex-col gap-2">
        {visibleButtons.map((state) => {
          const s = stateConfig[state]
          const active = botState === state
          return (
            <motion.button
              key={state}
              whileHover={{ scale: 1.06, x: -2 }}
              whileTap={{ scale: 0.94 }}
              onClick={() => setBotState(state)}
              className="flex items-center gap-2 px-5 py-2 rounded-2xl text-sm font-semibold cursor-pointer transition-all duration-300"
              style={
                active
                  ? {
                      background: s.hex,
                      color: '#fff',
                      boxShadow: `0 0 24px ${s.bg}, 0 4px 16px rgba(0,0,0,0.3)`,
                      border: `1px solid ${s.hex}`,
                    }
                  : {
                      background: 'rgba(0,0,0,0.25)',
                      backdropFilter: 'blur(12px)',
                      color: 'rgba(255,255,255,0.7)',
                      border: '1px solid rgba(255,255,255,0.15)',
                    }
              }
            >
              <span>{s.icon}</span>
              <span>{s.label}</span>
            </motion.button>
          )
        })}
      </div>
    </div>
  )
}
