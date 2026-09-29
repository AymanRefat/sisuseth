import { useEffect, useRef, useState } from "react";

export const formatMinutes = (minutes) => {
  const m = Math.round(minutes / 5) * 5;
  const h = Math.floor(m / 60);
  const rest = m % 60;
  return h ? (rest ? `${h} h ${rest} min` : `${h} h`) : `${rest} min`;
};

/** True once the element has scrolled into view (stays true). */
const DEFAULT_OPTIONS = { threshold: 0.3 };

export function useInView(options = DEFAULT_OPTIONS) {
  const ref = useRef(null);
  const [inView, setInView] = useState(false);
  useEffect(() => {
    if (!ref.current || inView) return;
    const observer = new IntersectionObserver(([entry]) => entry.isIntersecting && setInView(true), options);
    observer.observe(ref.current);
    return () => observer.disconnect();
  }, [inView, options]);
  return [ref, inView];
}

export const safeStorage = {
  get: (k) => { try { return localStorage.getItem(k); } catch { return null; } },
  set: (k, v) => { try { localStorage.setItem(k, v); } catch { /* unavailable */ } },
};
