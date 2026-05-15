/**
 * Microfondan to'g'ridan-to'g'ri WAV formatida yozib oluvchi klass.
 * MediaRecorder WebM ishlatadi (Azure Windows da qo'llab-quvvatlamaydi),
 * bu klass esa Web Audio API orqali raw PCM → WAV yaratadi.
 */

export class WavRecorder {
  private ctx: AudioContext
  private processor: ScriptProcessorNode
  private source: MediaStreamAudioSourceNode
  private samples: Float32Array[] = []
  readonly sampleRate: number

  constructor(stream: MediaStream) {
    // 16 kHz nutq tanib olish uchun optimal
    this.ctx = new AudioContext({ sampleRate: 16000 })
    this.sampleRate = this.ctx.sampleRate

    this.source    = this.ctx.createMediaStreamSource(stream)
    this.processor = this.ctx.createScriptProcessor(4096, 1, 1)

    // onaudioprocess ishlashi uchun destination ga ulash kerak, lekin ovoz chiqmasligi uchun gain=0
    const silent = this.ctx.createGain()
    silent.gain.value = 0

    this.processor.onaudioprocess = (e) => {
      const data = e.inputBuffer.getChannelData(0)
      this.samples.push(new Float32Array(data))
    }

    this.source.connect(this.processor)
    this.processor.connect(silent)
    silent.connect(this.ctx.destination)
  }

  /** Yozishni to'xtatib, WAV Blob qaytaradi */
  stop(): Blob {
    this.source.disconnect()
    this.processor.disconnect()
    void this.ctx.close()

    // Barcha chunklar bitta bufferga
    const totalLen = this.samples.reduce((n, s) => n + s.length, 0)
    const pcm = new Float32Array(totalLen)
    let offset = 0
    for (const chunk of this.samples) {
      pcm.set(chunk, offset)
      offset += chunk.length
    }

    return encodeWav(pcm, this.sampleRate)
  }
}

/** Float32 PCM massivini WAV formatida kodlaydi */
function encodeWav(samples: Float32Array, sampleRate: number): Blob {
  const buf  = new ArrayBuffer(44 + samples.length * 2)
  const view = new DataView(buf)

  const str = (off: number, s: string) =>
    [...s].forEach((c, i) => view.setUint8(off + i, c.charCodeAt(0)))

  str(0,  'RIFF')
  view.setUint32(4,  36 + samples.length * 2, true)
  str(8,  'WAVE')
  str(12, 'fmt ')
  view.setUint32(16, 16,           true)  // chunk size
  view.setUint16(20, 1,            true)  // PCM
  view.setUint16(22, 1,            true)  // mono
  view.setUint32(24, sampleRate,   true)
  view.setUint32(28, sampleRate * 2, true) // byte rate
  view.setUint16(32, 2,            true)  // block align
  view.setUint16(34, 16,           true)  // bits per sample
  str(36, 'data')
  view.setUint32(40, samples.length * 2, true)

  // Float32 → Int16 PCM
  for (let i = 0; i < samples.length; i++) {
    const s = Math.max(-1, Math.min(1, samples[i]))
    view.setInt16(44 + i * 2, s < 0 ? s * 0x8000 : s * 0x7fff, true)
  }

  return new Blob([buf], { type: 'audio/wav' })
}
