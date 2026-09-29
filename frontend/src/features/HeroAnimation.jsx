// Feature: hero_animation. A flat-pack box opens and a shelf builds itself (pure SVG + CSS, loops).
import { useI18n } from "../i18n.jsx";

export default function HeroAnimation() {
  const { t } = useI18n();
  return (
    <div className="hero-anim" role="img" aria-label={t("hero.animLabel")}>
      <svg viewBox="0 0 200 160" width="200" height="160">
        <g className="ha-box">
          <rect x="50" y="95" width="100" height="50" rx="3" fill="#d6a46b" stroke="#a8743d" strokeWidth="2" />
          <rect x="50" y="88" width="50" height="10" fill="#e3b680" stroke="#a8743d" strokeWidth="2" className="ha-flap-l" />
          <rect x="100" y="88" width="50" height="10" fill="#e3b680" stroke="#a8743d" strokeWidth="2" className="ha-flap-r" />
          <text x="100" y="126" textAnchor="middle" fontSize="12" fontWeight="700" fill="#7a4f22">SISUSETH</text>
        </g>
        <g className="ha-shelf" fill="#ea580c">
          <rect className="ha-p ha-p1" x="55" y="20" width="8" height="125" rx="2" />
          <rect className="ha-p ha-p2" x="137" y="20" width="8" height="125" rx="2" />
          <rect className="ha-p ha-p3" x="55" y="20" width="90" height="8" rx="2" />
          <rect className="ha-p ha-p4" x="55" y="60" width="90" height="8" rx="2" />
          <rect className="ha-p ha-p5" x="55" y="100" width="90" height="8" rx="2" />
          <rect className="ha-p ha-p6" x="55" y="137" width="90" height="8" rx="2" />
        </g>
        <text className="ha-check" x="165" y="35" fontSize="28">✅</text>
      </svg>
    </div>
  );
}
