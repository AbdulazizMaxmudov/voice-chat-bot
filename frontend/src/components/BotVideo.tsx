import { useEffect, useRef } from 'react'

interface Props {
  src: string
  className?: string
}

export default function BotVideo({ src, className }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const video = videoRef.current
    const canvas = canvasRef.current
    if (!video || !canvas) return

    const ctx = canvas.getContext('2d', { willReadFrequently: true })
    if (!ctx) return

    let animId: number

    function processFrame() {
      if (!video || !canvas || !ctx) return
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

      const frame = ctx.getImageData(0, 0, canvas.width, canvas.height)
      const d = frame.data

      for (let i = 0; i < d.length; i += 4) {
        const r = d[i]
        const g = d[i + 1]
        const b = d[i + 2]
        // Only pure white — channels must be bright AND very similar (not skin tones)
        const maxDiff = Math.max(Math.abs(r - g), Math.abs(g - b), Math.abs(r - b))
        if (r > 235 && g > 235 && b > 235 && maxDiff < 20) {
          d[i + 3] = 0
        }
      }

      ctx.putImageData(frame, 0, 0)
      animId = requestAnimationFrame(processFrame)
    }

    function onLoadedMetadata() {
      if (!video || !canvas) return
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
    }

    video.addEventListener('loadedmetadata', onLoadedMetadata)
    video.addEventListener('play', () => { animId = requestAnimationFrame(processFrame) })

    // autoPlay attribute alone can be blocked by browsers (especially on deploy).
    // Explicitly call play() and register unlock handlers on user interaction as fallback.
    void video.play().catch(() => {
      const unlock = () => {
        void video.play()
        document.removeEventListener('click', unlock)
        document.removeEventListener('touchstart', unlock)
      }
      document.addEventListener('click', unlock)
      document.addEventListener('touchstart', unlock)
    })

    return () => {
      cancelAnimationFrame(animId)
    }
  }, [src])

  return (
    <>
      <video
        ref={videoRef}
        src={src}
        autoPlay
        loop
        muted
        playsInline
        style={{ display: 'none' }}
      />
      <canvas ref={canvasRef} className={className} />
    </>
  )
}
