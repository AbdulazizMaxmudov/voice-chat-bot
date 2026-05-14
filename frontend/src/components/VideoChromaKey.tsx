import { useEffect, useRef } from 'react'
import bgVideo from '../video/mp_.mp4'

interface Props {
  className?: string
}

export default function VideoChromaKey({ className }: Props) {
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
        // Gray/neutral background: channels similar + mid brightness
        const maxDiff = Math.max(Math.abs(r - g), Math.abs(g - b), Math.abs(r - b))
        const avg = (r + g + b) / 3
        if (maxDiff < 30 && avg > 110 && avg < 220) {
          d[i + 3] = 0
        }
      }

      ctx.putImageData(frame, 0, 0)
      animId = requestAnimationFrame(processFrame)
    }

    function onPlay() {
      animId = requestAnimationFrame(processFrame)
    }

    function onLoadedMetadata() {
      if (!video || !canvas) return
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
    }

    video.addEventListener('loadedmetadata', onLoadedMetadata)
    video.addEventListener('play', onPlay)

    return () => {
      cancelAnimationFrame(animId)
      video.removeEventListener('loadedmetadata', onLoadedMetadata)
      video.removeEventListener('play', onPlay)
    }
  }, [])

  return (
    <>
      <video
        ref={videoRef}
        src={bgVideo}
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
