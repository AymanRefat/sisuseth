// Reading-progress bar drawn as a yellow tape measure that pulls out as you scroll.
import { useScroll } from "./motion.js";

export default function ScrollTape() {
  const { progress } = useScroll();
  const cm = Math.round(progress * 300);
  return (
    <div className="tape" aria-hidden="true">
      <div className="tape-fill" style={{ width: `${progress * 100}%` }}>
        {progress > 0.02 && <span className="tape-readout">{cm} cm</span>}
      </div>
    </div>
  );
}
