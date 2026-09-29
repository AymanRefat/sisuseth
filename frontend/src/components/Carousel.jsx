// Horizontal slider for long lists (reviews, videos, before/after).
// Native scroll-snap (swipe on phones, trackpad on laptops) + arrows + dots.
// Arrows and dots only appear when there is more than fits on screen.
import { Children, useCallback, useEffect, useRef, useState } from "react";
import { useI18n } from "../i18n.jsx";

const prefersReducedMotion = () => window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;

export default function Carousel({ children, autoPlayMs = 0, className = "", label }) {
  const { t } = useI18n();
  const track = useRef(null);
  const [pages, setPages] = useState(1);
  const [page, setPage] = useState(0);
  const [paused, setPaused] = useState(false);
  const count = Children.count(children);

  const measure = useCallback(() => {
    const el = track.current;
    if (!el) return;
    setPages(Math.max(1, Math.ceil(el.scrollWidth / el.clientWidth - 0.05)));
    const atEnd = el.scrollLeft + el.clientWidth >= el.scrollWidth - 4;
    setPage(atEnd ? Math.ceil(el.scrollWidth / el.clientWidth - 0.05) - 1 : Math.round(el.scrollLeft / el.clientWidth));
  }, []);

  useEffect(() => {
    measure();
    const observer = new ResizeObserver(measure);
    observer.observe(track.current);
    return () => observer.disconnect();
  }, [measure, count]);

  const goTo = useCallback((p) => {
    const el = track.current;
    const target = (p + pages) % pages;
    el.scrollTo({ left: target * el.clientWidth, behavior: prefersReducedMotion() ? "auto" : "smooth" });
  }, [pages]);

  useEffect(() => {
    if (!autoPlayMs || paused || pages < 2 || prefersReducedMotion()) return;
    const id = setInterval(() => goTo(page + 1), autoPlayMs);
    return () => clearInterval(id);
  }, [autoPlayMs, paused, pages, page, goTo]);

  const scrollable = pages > 1;
  return (
    <div className={`carousel ${className}`} aria-roledescription="carousel" aria-label={label}
         onMouseEnter={() => setPaused(true)} onMouseLeave={() => setPaused(false)}
         onFocus={() => setPaused(true)} onBlur={() => setPaused(false)} onTouchStart={() => setPaused(true)}>
      <div className="carousel-track" ref={track} onScroll={measure}>
        {Children.map(children, (child) => <div className="carousel-item">{child}</div>)}
      </div>
      {scrollable && (
        <div className="carousel-nav">
          <button className="carousel-arrow" onClick={() => goTo(page - 1)} aria-label={t("ui.previous")}>‹</button>
          <div className="carousel-dots">
            {Array.from({ length: pages }, (_, i) => (
              <button key={i} className={i === page ? "active" : ""} onClick={() => goTo(i)}
                      aria-label={`${i + 1} / ${pages}`} aria-current={i === page} />
            ))}
          </div>
          <button className="carousel-arrow" onClick={() => goTo(page + 1)} aria-label={t("ui.next")}>›</button>
        </div>
      )}
    </div>
  );
}
