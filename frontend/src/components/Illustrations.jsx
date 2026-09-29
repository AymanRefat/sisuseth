// Hand-drawn style furniture line art (inline SVG, colours come from CSS variables).
const common = { fill: "none", stroke: "currentColor", strokeWidth: 3, strokeLinecap: "round", strokeLinejoin: "round" };

export const Lamp = (props) => (
  <svg viewBox="0 0 80 160" {...props} aria-hidden="true">
    <g {...common}>
      <line x1="40" y1="0" x2="40" y2="70" />
      <path d="M18 100 L28 70 H52 L62 100 Z" fill="var(--oak-light)" />
      <circle cx="40" cy="108" r="5" fill="var(--sun)" stroke="none" className="lamp-bulb" />
    </g>
  </svg>
);

export const Chair = (props) => (
  <svg viewBox="0 0 120 150" {...props} aria-hidden="true">
    <g {...common}>
      <path d="M30 10 Q60 0 90 10 L86 70 H34 Z" fill="var(--oak-light)" />
      <path d="M22 72 H98 L94 88 H26 Z" fill="var(--oak)" />
      <line x1="32" y1="88" x2="24" y2="146" /><line x1="88" y1="88" x2="96" y2="146" />
      <line x1="44" y1="88" x2="46" y2="140" /><line x1="76" y1="88" x2="74" y2="140" />
    </g>
  </svg>
);

export const Plant = (props) => (
  <svg viewBox="0 0 100 150" {...props} aria-hidden="true">
    <g {...common}>
      <path d="M30 100 H70 L64 146 H36 Z" fill="var(--terracotta)" />
      <g className="plant-leaves" stroke="var(--leaf)">
        <path d="M50 100 C50 70 30 60 18 40 C40 44 52 62 50 100" fill="var(--leaf-light)" />
        <path d="M50 100 C52 64 70 50 84 30 C80 58 62 72 50 100" fill="var(--leaf-light)" />
        <path d="M50 100 C48 70 50 40 50 14 C60 40 58 72 50 100" fill="var(--leaf-light)" />
      </g>
    </g>
  </svg>
);

export const Shelf = (props) => (
  <svg viewBox="0 0 140 150" {...props} aria-hidden="true">
    <g {...common}>
      <rect x="10" y="6" width="120" height="140" rx="4" fill="var(--oak-light)" />
      <line x1="10" y1="52" x2="130" y2="52" /><line x1="10" y1="98" x2="130" y2="98" />
      <rect x="22" y="22" width="10" height="30" fill="var(--terracotta)" /><rect x="34" y="18" width="10" height="34" fill="var(--sun)" />
      <rect x="46" y="26" width="10" height="26" fill="var(--leaf-light)" />
      <circle cx="100" cy="80" r="12" fill="var(--cream)" />
      <rect x="30" y="112" width="40" height="34" rx="3" fill="var(--cream)" />
    </g>
  </svg>
);

/** Screw head used for step numbers and bullet points. */
export const Screw = ({ className = "" }) => (
  <svg viewBox="0 0 40 40" className={`screw ${className}`} aria-hidden="true">
    <defs>
      <radialGradient id="screw-metal" cx="35%" cy="30%" r="75%">
        <stop offset="0" stopColor="#ffffff" /><stop offset=".45" stopColor="#d6dbe1" /><stop offset="1" stopColor="#8d959f" />
      </radialGradient>
    </defs>
    <circle cx="20" cy="20" r="18" fill="url(#screw-metal)" stroke="#7b838d" strokeWidth="1.5" />
    <circle cx="20" cy="20" r="13.5" fill="none" stroke="rgba(0,0,0,.08)" strokeWidth="1" />
    <path d="M13 20 H27 M20 13 V27" stroke="#5d646d" strokeWidth="3" strokeLinecap="round" />
    <path d="M13.5 21 H27 M21 13.5 V27" stroke="rgba(255,255,255,.6)" strokeWidth="1" strokeLinecap="round" />
  </svg>
);

/** A hand-drawn underline that draws itself under a highlighted word. */
export const Scribble = () => (
  <svg viewBox="0 0 300 20" preserveAspectRatio="none" className="scribble" aria-hidden="true">
    <path d="M4 14 C60 4 120 18 180 8 S270 6 296 12" fill="none" stroke="var(--brand)" strokeWidth="6" strokeLinecap="round" />
  </svg>
);
