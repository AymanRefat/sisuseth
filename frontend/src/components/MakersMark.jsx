// Developer credit, styled as a furniture maker's burned-in stamp.
// Not managed in the CMS on purpose, so the site owner cannot remove it by accident.
import { useInView } from "../features/utils.js";

const LINKEDIN = "https://www.linkedin.com/in/aymanrefat/";
const RING = "CRAFTED BY AYMAN REFAT • WEB DEVELOPER • ";

export default function MakersMark() {
  const [ref, inView] = useInView({ threshold: 0.6 });
  return (
    <a ref={ref} href={LINKEDIN} target="_blank" rel="noopener noreferrer"
       className={`makers-mark ${inView ? "stamped" : ""}`}
       aria-label="Website crafted by Ayman Refat – LinkedIn profile">
      <span className="mm-burn" aria-hidden="true" />
      <svg viewBox="0 0 200 200" className="mm-seal" aria-hidden="true">
        <defs>
          <path id="mm-circle" d="M100,100 m-72,0 a72,72 0 1,1 144,0 a72,72 0 1,1 -144,0" />
        </defs>
        <circle cx="100" cy="100" r="94" className="mm-rim" />
        <circle cx="100" cy="100" r="54" className="mm-inner" />
        <g className="mm-ring">
          <text className="mm-ring-text"><textPath href="#mm-circle" textLength="452">{RING}</textPath></text>
        </g>
        {/* mallet */}
        <g className="mm-mallet" transform="translate(100 96) rotate(-35)">
          <rect x="-4" y="-6" width="8" height="46" rx="3" />
          <rect x="-20" y="-24" width="40" height="22" rx="5" />
        </g>
        <text x="100" y="138" className="mm-year">EST. {new Date().getFullYear()}</text>
      </svg>
      <span className="mm-caption">
        <small>Developed by</small>
        <strong>Ayman Refat</strong>
        <span className="mm-link">LinkedIn ↗</span>
      </span>
    </a>
  );
}
