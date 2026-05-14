import { useEffect, useRef } from 'react'
import botGif from '../video/Untitled design.gif'

interface Props {
  className?: string
}

export default function GifTransparent({ className }: Props) {
  const imgRef = useRef<HTMLImageElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const img = imgRef.current
    const canvas = canvasRef.current
    if (!img || !canvas) return

    const ctx = canvas.getContext('2d', { willReadFrequently: true })
    if (!ctx) return

    let animId: number

    function processFrame() {
      if (!img || !canvas || !ctx) return

      canvas.width = img.naturalWidth || img.width
      canvas.height = img.naturalHeight || img.height

      ctx.drawImage(img, 0, 0, canvas.width, canvas.height)

      const frame = ctx.getImageData(0, 0, canvas.width, canvas.height)
      const d = frame.data

      for (let i = 0; i < d.length; i += 4) {
        const r = d[i]
        const g = d[i + 1]
        const b = d[i + 2]
        // Remove white and near-white pixels
        if (r > 210 && g > 210 && b > 210) {
          const whiteness = (r + g + b) / 3
          d[i + 3] = Math.round(Math.max(0, 255 - whiteness) * 2)
        }
      }

      ctx.putImageData(frame, 0, 0)
      animId = requestAnimationFrame(processFrame)
    }

    function start() {
      animId = requestAnimationFrame(processFrame)
    }

    if (img.complete) {
      start()
    } else {
      img.addEventListener('load', start)
    }

    return () => {
      cancelAnimationFrame(animId)
      img.removeEventListener('load', start)
    }
  }, [])

  return (
    <>
      <img
        ref={imgRef}
        src={botGif}
        alt=""
        style={{ position: 'absolute', left: '-9999px', top: '-9999px' }}
      />
      <canvas ref={canvasRef} className={className} />
    </>
  )
}
