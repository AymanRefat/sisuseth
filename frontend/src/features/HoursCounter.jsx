// Feature: hours_counter. Counts up to the number of weekend hours saved when scrolled into view.
import { useEffect, useState } from "react";
import { useI18n } from "../i18n.jsx";
import { useInView } from "./utils.js";

export default function HoursCounter({ hours, areas }) {
  const { t } = useI18n();
  const [ref, inView] = useInView();
  const [shown, setShown] = useState(0);

  useEffect(() => {
    if (!inView) return;
    const start = performance.now();
    const duration = 1800;
    let frame;
    const tick = (now) => {
      const p = Math.min(1, (now - start) / duration);
      setShown(Math.round(hours * (1 - (1 - p) ** 3)));
      if (p < 1) frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [inView, hours]);

  return (
    <div ref={ref} className="hours-counter">
      <span className="hours-number">{shown.toLocaleString("fi-FI")}</span>
      <span>{t("hours.label", { areas })}</span>
    </div>
  );
}
