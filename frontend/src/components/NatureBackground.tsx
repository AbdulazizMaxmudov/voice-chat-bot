import bgImage from '../video/bg.jpg'

export default function NatureBackground() {
  return (
    <img
      src={bgImage}
      className="absolute inset-0 w-full h-full object-cover"
      alt=""
    />
  )
}
