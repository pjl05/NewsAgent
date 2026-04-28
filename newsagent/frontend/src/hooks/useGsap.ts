import { useEffect, useRef } from 'react'
import gsap from 'gsap'

export function useGsap() {
  const ctxRef = useRef<gsap.Context | null>(null)

  useEffect(() => {
    ctxRef.current = gsap.context(() => {
      // GSAP animations will be added here by staggerCards
    })
    return () => ctxRef.current?.revert()
  }, [])

  const staggerCards = (selector: string) => {
    ctxRef.current?.add(() => {
      gsap.from(selector, {
        y: 60,
        opacity: 0,
        scale: 0.95,
        duration: 0.6,
        stagger: 0.1,
        ease: 'back.out(1.7)',
      })
    })
  }

  return { staggerCards }
}
