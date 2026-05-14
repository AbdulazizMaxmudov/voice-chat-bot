import { motion, AnimatePresence } from 'framer-motion'
import type { BotState } from '../App'

interface Props {
  state: BotState
}

const stateColors = {
  listening: { primary: '#10b981', glow: 'rgba(16,185,129,0.4)', ring: '#6ee7b7' },
  thinking:  { primary: '#f59e0b', glow: 'rgba(245,158,11,0.4)',  ring: '#fcd34d' },
  speaking:  { primary: '#3b82f6', glow: 'rgba(59,130,246,0.4)',  ring: '#93c5fd' },
}

/* Listening: mic waves around the bot */
function ListeningWaves({ color }: { color: string }) {
  return (
    <>
      {[1, 2, 3].map((i) => (
        <motion.div
          key={i}
          className="absolute inset-0 rounded-full border-2"
          style={{ borderColor: color }}
          initial={{ scale: 1, opacity: 0.7 }}
          animate={{ scale: 1 + i * 0.28, opacity: 0 }}
          transition={{ duration: 2, repeat: Infinity, delay: i * 0.5, ease: 'easeOut' }}
        />
      ))}
    </>
  )
}

/* Speaking: vertical bars */
function SpeakingBars({ color }: { color: string }) {
  const heights = [14, 22, 32, 22, 14, 28, 18]
  return (
    <div className="flex items-center gap-1">
      {heights.map((h, i) => (
        <motion.div
          key={i}
          className="w-1.5 rounded-full"
          style={{ backgroundColor: color }}
          animate={{ height: [h * 0.5, h, h * 0.5] }}
          transition={{ duration: 0.5, repeat: Infinity, delay: i * 0.08, ease: 'easeInOut' }}
        />
      ))}
    </div>
  )
}

/* Thinking: orbiting dots */
function ThinkingOrbit({ color }: { color: string }) {
  return (
    <>
      {[0, 120, 240].map((deg, i) => (
        <motion.div
          key={i}
          className="absolute w-3 h-3 rounded-full"
          style={{ backgroundColor: color, top: '50%', left: '50%', marginTop: -6, marginLeft: -6 }}
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: 'linear', delay: i * 0.15 }}
          transformTemplate={({ rotate }) =>
            `rotate(${rotate}) translateX(54px) rotate(-${rotate})`
          }
        />
      ))}
    </>
  )
}

export default function BotCharacter({ state }: Props) {
  const colors = stateColors[state]

  return (
    <div className="flex flex-col items-center gap-6 select-none">

      {/* Glow + ring wrapper */}
      <div className="relative flex items-center justify-center">

        {/* Outer ambient glow */}
        <motion.div
          className="absolute rounded-full"
          style={{
            width: 220, height: 220,
            background: `radial-gradient(circle, ${colors.glow} 0%, transparent 70%)`,
          }}
          animate={{ scale: [1, 1.15, 1], opacity: [0.6, 1, 0.6] }}
          transition={{ duration: 2.5, repeat: Infinity, ease: 'easeInOut' }}
        />

        {/* Listening pulse rings */}
        {state === 'listening' && (
          <div className="absolute" style={{ width: 180, height: 180 }}>
            <ListeningWaves color={colors.ring} />
          </div>
        )}

        {/* Thinking orbit */}
        {state === 'thinking' && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="relative" style={{ width: 180, height: 180 }}>
              <ThinkingOrbit color={colors.primary} />
            </div>
          </div>
        )}

        {/* Robot body */}
        <motion.div
          animate={
            state === 'speaking'
              ? { y: [0, -8, 0] }
              : state === 'thinking'
              ? { rotate: [-4, 4, -4] }
              : { y: [0, -5, 0] }
          }
          transition={{
            duration: state === 'speaking' ? 0.45 : state === 'thinking' ? 2.5 : 3,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          className="relative z-10"
        >
          <svg width="160" height="200" viewBox="0 0 160 200" fill="none" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="bodyGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#1e293b" />
                <stop offset="100%" stopColor="#0f172a" />
              </linearGradient>
              <linearGradient id="headGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#334155" />
                <stop offset="100%" stopColor="#1e293b" />
              </linearGradient>
              <filter id="glow">
                <feGaussianBlur stdDeviation="3" result="blur" />
                <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
              </filter>
            </defs>

            {/* Antenna */}
            <rect x="77" y="4" width="6" height="22" rx="3" fill="#475569" />
            <motion.circle
              cx="80" cy="4" r="6" fill={colors.primary}
              animate={{ opacity: [0.6, 1, 0.6], r: [5, 7, 5] }}
              transition={{ duration: 1.2, repeat: Infinity, ease: 'easeInOut' }}
              filter="url(#glow)"
            />

            {/* Head */}
            <rect x="28" y="24" width="104" height="80" rx="22" fill="url(#headGrad)" />
            {/* Head highlight */}
            <rect x="32" y="28" width="96" height="30" rx="16" fill="rgba(255,255,255,0.05)" />

            {/* Eyes */}
            <motion.g filter="url(#glow)">
              {/* Left eye */}
              <rect x="44" y="48" width="28" height="20" rx="10" fill="#0f172a" />
              <motion.rect
                x="47" y="51" width="22" height="14" rx="7"
                fill={colors.primary}
                animate={state === 'thinking' ? { scaleX: [1, 0.4, 1] } : { opacity: [0.8, 1, 0.8] }}
                transition={{ duration: state === 'thinking' ? 1.5 : 1.5, repeat: Infinity }}
              />
              <circle cx="61" cy="57" r="3" fill="white" opacity="0.6" />

              {/* Right eye */}
              <rect x="88" y="48" width="28" height="20" rx="10" fill="#0f172a" />
              <motion.rect
                x="91" y="51" width="22" height="14" rx="7"
                fill={colors.primary}
                animate={state === 'thinking' ? { scaleX: [1, 0.4, 1] } : { opacity: [0.8, 1, 0.8] }}
                transition={{ duration: state === 'thinking' ? 1.5 : 1.5, repeat: Infinity, delay: 0.2 }}
              />
              <circle cx="105" cy="57" r="3" fill="white" opacity="0.6" />
            </motion.g>

            {/* Mouth */}
            <rect x="52" y="82" width="56" height="12" rx="6" fill="#0f172a" />
            <AnimatePresence mode="wait">
              {state === 'speaking' ? (
                <motion.rect
                  key="speaking-mouth"
                  x="55" y="84" rx="4"
                  fill={colors.primary}
                  animate={{ width: [10, 46, 10], x: [55, 57, 55], height: [8, 8, 8] }}
                  transition={{ duration: 0.35, repeat: Infinity }}
                />
              ) : state === 'thinking' ? (
                <motion.rect
                  key="thinking-mouth"
                  x="60" y="85" width="20" height="6" rx="3"
                  fill={colors.primary}
                  initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                />
              ) : (
                <motion.rect
                  key="listening-mouth"
                  x="55" y="84" width="50" height="8" rx="4"
                  fill={colors.primary}
                  initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                />
              )}
            </AnimatePresence>

            {/* Side panels / ears */}
            <rect x="14" y="38" width="16" height="36" rx="8" fill="#1e293b" />
            <rect x="130" y="38" width="16" height="36" rx="8" fill="#1e293b" />
            <motion.rect
              x="17" y="44" width="10" height="10" rx="5"
              fill={colors.primary}
              animate={{ opacity: [0.4, 1, 0.4] }}
              transition={{ duration: 1, repeat: Infinity }}
            />
            <motion.rect
              x="133" y="44" width="10" height="10" rx="5"
              fill={colors.primary}
              animate={{ opacity: [0.4, 1, 0.4] }}
              transition={{ duration: 1, repeat: Infinity, delay: 0.5 }}
            />

            {/* Neck */}
            <rect x="66" y="102" width="28" height="14" rx="6" fill="#1e293b" />
            <rect x="70" y="104" width="20" height="6" rx="3" fill="#0f172a" />

            {/* Body */}
            <rect x="22" y="114" width="116" height="80" rx="20" fill="url(#bodyGrad)" />
            {/* Body highlight */}
            <rect x="26" y="118" width="108" height="24" rx="14" fill="rgba(255,255,255,0.04)" />

            {/* Chest panel */}
            <rect x="44" y="130" width="72" height="44" rx="12" fill="#0f172a" />

            {/* Chest indicators */}
            <motion.circle cx="62" cy="144" r="6" fill={colors.primary}
              animate={{ opacity: [0.5, 1, 0.5] }}
              transition={{ duration: 1.2, repeat: Infinity }}
              filter="url(#glow)"
            />
            <motion.circle cx="80" cy="144" r="6" fill={colors.primary}
              animate={{ opacity: [0.5, 1, 0.5] }}
              transition={{ duration: 1.2, repeat: Infinity, delay: 0.4 }}
              filter="url(#glow)"
            />
            <motion.circle cx="98" cy="144" r="6" fill={colors.primary}
              animate={{ opacity: [0.5, 1, 0.5] }}
              transition={{ duration: 1.2, repeat: Infinity, delay: 0.8 }}
              filter="url(#glow)"
            />

            {/* Chest bar */}
            <rect x="52" y="158" width="56" height="8" rx="4" fill="#1e293b" />
            <motion.rect
              x="52" y="158" height="8" rx="4"
              fill={colors.primary}
              animate={{ width: [10, 56, 10] }}
              transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
            />

            {/* Arms */}
            <motion.g
              animate={state === 'speaking' ? { rotate: [-12, 12, -12] } : { rotate: [0, 4, 0] }}
              transition={{ duration: state === 'speaking' ? 0.45 : 3, repeat: Infinity, ease: 'easeInOut' }}
              style={{ originX: '22px', originY: '130px' }}
            >
              <rect x="4" y="118" width="20" height="52" rx="10" fill="#1e293b" />
              <rect x="4" y="162" width="20" height="14" rx="7" fill="#0f172a" />
            </motion.g>

            <motion.g
              animate={state === 'speaking' ? { rotate: [12, -12, 12] } : { rotate: [0, -4, 0] }}
              transition={{ duration: state === 'speaking' ? 0.45 : 3, repeat: Infinity, ease: 'easeInOut' }}
              style={{ originX: '138px', originY: '130px' }}
            >
              <rect x="136" y="118" width="20" height="52" rx="10" fill="#1e293b" />
              <rect x="136" y="162" width="20" height="14" rx="7" fill="#0f172a" />
            </motion.g>

            {/* Shadow */}
            <ellipse cx="80" cy="198" rx="48" ry="5" fill="rgba(0,0,0,0.2)" />
          </svg>
        </motion.div>
      </div>

      {/* Speaking bars below */}
      <AnimatePresence>
        {state === 'speaking' && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 8 }}
          >
            <SpeakingBars color={colors.primary} />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Name badge */}
      <motion.div
        className="px-8 py-3 rounded-2xl font-bold text-base tracking-widest uppercase"
        style={{
          background: 'rgba(0,0,0,0.35)',
          backdropFilter: 'blur(12px)',
          border: `1px solid ${colors.primary}40`,
          color: colors.ring,
          boxShadow: `0 0 20px ${colors.glow}`,
        }}
        animate={{ boxShadow: [`0 0 20px ${colors.glow}`, `0 0 35px ${colors.glow}`, `0 0 20px ${colors.glow}`] }}
        transition={{ duration: 2, repeat: Infinity }}
      >
        Eco Assistant
      </motion.div>
    </div>
  )
}
