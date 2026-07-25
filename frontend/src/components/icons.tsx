import type { SVGProps } from 'react'

type IconProps = SVGProps<SVGSVGElement>

function base(props: IconProps) {
  return {
    width: 20,
    height: 20,
    viewBox: '0 0 24 24',
    fill: 'none',
    stroke: 'currentColor',
    strokeWidth: 1.75,
    strokeLinecap: 'round' as const,
    strokeLinejoin: 'round' as const,
    ...props,
  }
}

export function IconScan(p: IconProps) {
  return (
    <svg {...base(p)}>
      <path d="M3 7V5a2 2 0 0 1 2-2h2" />
      <path d="M17 3h2a2 2 0 0 1 2 2v2" />
      <path d="M21 17v2a2 2 0 0 1-2 2h-2" />
      <path d="M7 21H5a2 2 0 0 1-2-2v-2" />
      <rect x="7" y="7" width="10" height="10" rx="1" />
    </svg>
  )
}

export function IconChart(p: IconProps) {
  return (
    <svg {...base(p)}>
      <path d="M4 19V5" />
      <path d="M4 19h16" />
      <path d="M8 16v-5" />
      <path d="M12 16V8" />
      <path d="M16 16v-3" />
    </svg>
  )
}

export function IconDoc(p: IconProps) {
  return (
    <svg {...base(p)}>
      <path d="M14 2H7a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z" />
      <path d="M14 2v6h6" />
      <path d="M9 13h6" />
      <path d="M9 17h4" />
    </svg>
  )
}

export function IconChecklist(p: IconProps) {
  return (
    <svg {...base(p)}>
      <path d="M9 6h11" />
      <path d="M9 12h11" />
      <path d="M9 18h11" />
      <path d="M4 6h.01" />
      <path d="M4 12h.01" />
      <path d="M4 18h.01" />
    </svg>
  )
}

export function IconOrg(p: IconProps) {
  return (
    <svg {...base(p)}>
      <circle cx="12" cy="5" r="2.5" />
      <circle cx="5" cy="18" r="2.5" />
      <circle cx="19" cy="18" r="2.5" />
      <path d="M12 7.5v3.5" />
      <path d="M12 11h7v4.5" />
      <path d="M12 11H5v4.5" />
    </svg>
  )
}

export function IconSliders(p: IconProps) {
  return (
    <svg {...base(p)}>
      <path d="M4 7h10" />
      <path d="M18 7h2" />
      <circle cx="16" cy="7" r="2" />
      <path d="M4 17h2" />
      <path d="M10 17h10" />
      <circle cx="8" cy="17" r="2" />
    </svg>
  )
}

export function IconHelp(p: IconProps) {
  return (
    <svg {...base(p)}>
      <circle cx="12" cy="12" r="9" />
      <path d="M9.5 9.5a2.5 2.5 0 1 1 3.6 2.25c-.7.35-1.1.85-1.1 1.75" />
      <path d="M12 17h.01" />
    </svg>
  )
}

export function IconPower(p: IconProps) {
  return (
    <svg {...base(p)}>
      <path d="M12 3v8" />
      <path d="M7.5 6.5a7 7 0 1 0 9 0" />
    </svg>
  )
}

export function IconLive(p: IconProps) {
  return (
    <svg {...base(p)}>
      <circle cx="12" cy="12" r="3" />
      <path d="M5 12a7 7 0 0 1 14 0" />
      <path d="M2 12a10 10 0 0 1 20 0" />
    </svg>
  )
}

export function IconChevron(p: IconProps) {
  return (
    <svg {...base({ width: 14, height: 14, ...p })}>
      <path d="M9 6l5 5-5 5" />
    </svg>
  )
}

export function IconFilter(p: IconProps) {
  return (
    <svg {...base({ width: 16, height: 16, ...p })}>
      <path d="M4 5h16l-6 7v5l-4 2v-7L4 5z" />
    </svg>
  )
}

export function IconForklift(p: IconProps) {
  return (
    <svg {...base({ width: 28, height: 28, ...p })}>
      <path d="M3 17h10v-6H8" />
      <path d="M13 17h3l3-5h2" />
      <circle cx="7" cy="19" r="1.5" />
      <circle cx="15" cy="19" r="1.5" />
      <path d="M8 11V7h6" />
    </svg>
  )
}

export function IconImpact(p: IconProps) {
  return (
    <svg {...base({ width: 28, height: 28, ...p })}>
      <circle cx="8" cy="14" r="3" />
      <path d="M11 14h5l3-3" />
      <path d="M16 11v6" />
      <path d="M19 8l2 2-2 2" />
    </svg>
  )
}

export function IconClock(p: IconProps) {
  return (
    <svg {...base({ width: 28, height: 28, ...p })}>
      <circle cx="12" cy="12" r="8" />
      <path d="M12 8v4l3 2" />
    </svg>
  )
}

export function IconCube(p: IconProps) {
  return (
    <svg {...base({ width: 28, height: 28, ...p })}>
      <path d="M12 3l8 4.5v9L12 21l-8-4.5v-9L12 3z" />
      <path d="M12 12l8-4.5" />
      <path d="M12 12v9" />
      <path d="M12 12L4 7.5" />
    </svg>
  )
}

export function IconHardhat(p: IconProps) {
  return (
    <svg {...base({ width: 28, height: 28, ...p })}>
      <path d="M4 15h16v2H4z" />
      <path d="M6 15a6 6 0 0 1 12 0" />
      <path d="M10 9h4" />
    </svg>
  )
}

export function IconFlag(p: IconProps) {
  return (
    <svg width={18} height={12} viewBox="0 0 18 12" {...p}>
      <rect width="18" height="12" rx="1" fill="#B22234" />
      <path
        fill="#fff"
        d="M0 2h18v1.2H0zm0 2.4h18v1.2H0zm0 2.4h18v1.2H0zm0 2.4h18V12H0z"
      />
      <rect width="7.5" height="6.5" fill="#3C3B6E" />
    </svg>
  )
}
