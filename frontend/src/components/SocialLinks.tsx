import type { ReactNode } from 'react'
import type { SocialLink } from '../types/api'

const labels: Record<string, string> = {
  FACEBOOK: 'Facebook',
  INSTAGRAM: 'Instagram',
  LINKEDIN: 'LinkedIn',
  X: 'X',
  TWITTER: 'Twitter',
  YOUTUBE: 'YouTube',
  WHATSAPP: 'WhatsApp',
  WEBSITE: 'Website',
}

export function SocialIcon({ platform }: { platform: string }): ReactNode {
  const p = platform.toUpperCase()
  const common = { width: 18, height: 18, viewBox: '0 0 24 24', fill: 'none', 'aria-hidden': true as const }

  switch (p) {
    case 'INSTAGRAM':
      return <svg {...common} viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="5" stroke="currentColor" strokeWidth="2"/><circle cx="12" cy="12" r="4" stroke="currentColor" strokeWidth="2"/><circle cx="17.5" cy="6.5" r="1.1" fill="currentColor"/></svg>
    case 'FACEBOOK':
      return <svg {...common}><path fill="currentColor" d="M13.5 21v-8h2.7l.4-3h-3.1V8.1c0-.9.3-1.5 1.6-1.5h1.7V3.9c-.3 0-1.3-.1-2.5-.1-2.5 0-4.2 1.5-4.2 4.3V10H7.4v3h2.7v8h3.4Z"/></svg>
    case 'LINKEDIN':
      return <svg {...common}><path fill="currentColor" d="M5.2 8.1H2.1V21h3.1V8.1ZM3.65 3A1.85 1.85 0 1 0 3.65 6.7 1.85 1.85 0 0 0 3.65 3ZM21 13.6c0-3.9-2.1-5.7-4.9-5.7-2.3 0-3.3 1.3-3.9 2.1V8.1H9.1V21h3.1v-6.4c0-1.7.3-3.4 2.5-3.4 2.1 0 2.1 2 2.1 3.5V21H20l1-7.4Z"/></svg>
    case 'YOUTUBE':
      return <svg {...common}><path fill="currentColor" d="M23.5 6.2a3 3 0 0 0-2.1-2.1C19.5 3.6 12 3.6 12 3.6s-7.5 0-9.4.5A3 3 0 0 0 .5 6.2 31 31 0 0 0 0 12a31 31 0 0 0 .5 5.8 3 3 0 0 0 2.1 2.1c1.9.5 9.4.5 9.4.5s7.5 0 9.4-.5a3 3 0 0 0 2.1-2.1A31 31 0 0 0 24 12a31 31 0 0 0-.5-5.8ZM9.6 15.6V8.4l6.3 3.6-6.3 3.6Z"/></svg>
    case 'WHATSAPP':
      return <svg {...common}><path fill="currentColor" d="M20.5 3.5A11.8 11.8 0 0 0 12.1 0C5.5 0 .2 5.3.2 11.9c0 2.1.6 4.1 1.6 5.9L.1 24l6.4-1.7a12 12 0 0 0 5.6 1.4h.1c6.5 0 11.8-5.3 11.8-11.8 0-3.2-1.2-6.2-3.5-8.4ZM12.2 21.6h-.1a9.7 9.7 0 0 1-5-1.4l-.4-.2-3.8 1 1-3.7-.2-.4a9.6 9.6 0 0 1-1.5-5.1c0-5.4 4.4-9.8 9.9-9.8 2.6 0 5.1 1 7 2.9a9.7 9.7 0 0 1 2.9 7c0 5.3-4.4 9.7-9.8 9.7Zm5.4-7.3c-.3-.2-1.8-.9-2.1-1-.3-.1-.5-.2-.7.2-.2.3-.8 1-.9 1.2-.2.2-.3.2-.6.1-1.6-.8-2.7-1.5-3.8-3.3-.3-.5.3-.5.8-1.6.1-.2.1-.4 0-.6-.1-.2-.7-1.7-1-2.3-.3-.6-.5-.5-.7-.5h-.6c-.2 0-.6.1-.9.4-.3.3-1.1 1.1-1.1 2.6s1.1 3 1.3 3.2c.2.2 2.1 3.3 5.2 4.6 1.9.8 2.6.8 3.5.7.6-.1 1.8-.7 2-1.4.3-.7.3-1.3.2-1.4-.1-.1-.3-.2-.6-.3Z"/></svg>
    case 'X':
    case 'TWITTER':
      return <svg {...common}><path fill="currentColor" d="M18.9 2H22l-6.8 7.8L23 22h-6.1l-4.8-6.3L6.6 22H3.5l7.2-8.3L1 2h6.3l4.3 5.7L18.9 2Zm-1.1 17.8h1.7L6.3 4.1H4.5l13.3 15.7Z"/></svg>
    default:
      return <svg {...common}><path fill="currentColor" d="M13 3h8v8h-2V6.4l-9.3 9.3-1.4-1.4L17.6 5H13V3ZM5 5h5v2H7v10h10v-3h2v5H5V5Z"/></svg>
  }
}

function iconClass(platform: string) {
  const p = platform.toUpperCase()
  switch (p) {
    case 'INSTAGRAM': return 'ra-social-icon ra-social-instagram'
    case 'FACEBOOK': return 'ra-social-icon ra-social-facebook'
    case 'YOUTUBE': return 'ra-social-icon ra-social-youtube'
    case 'WHATSAPP': return 'ra-social-icon ra-social-whatsapp'
    case 'LINKEDIN': return 'ra-social-icon ra-social-linkedin'
    case 'X':
    case 'TWITTER': return 'ra-social-icon ra-social-x'
    default: return 'ra-social-icon ra-social-default'
  }
}

export function SocialLinks({ links, onClick }: { links: SocialLink[]; onClick: (link: SocialLink) => void }) {
  const enabled = links.filter((link) => link.enabled).sort((a, b) => a.display_order - b.display_order)
  if (!enabled.length) return null

  return (
    <section className="mt-8 border-t border-slate-100 pt-7" aria-label="Social links">
      <div className="text-center">
        <p className="ra-eyebrow">Stay connected</p>
        <h2 className="mt-1 text-sm font-bold text-slate-950">Connect with us</h2>
      </div>
      <div className="mt-4 flex flex-wrap justify-center gap-2.5">
        {enabled.map((link) => {
          const platform = link.platform.toUpperCase()
          return (
            <a key={link.id} href={link.url} target="_blank" rel="noreferrer" onClick={() => onClick(link)} className="ra-button ra-button-secondary min-h-11 px-4">
              <span className={iconClass(platform)} aria-hidden="true">
                <SocialIcon platform={platform} />
              </span>
              {labels[platform] || link.platform}
            </a>
          )
        })}
      </div>
    </section>
  )
}
