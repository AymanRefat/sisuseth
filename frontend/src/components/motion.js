// Small motion helpers shared by the page. All of them do nothing for visitors who ask for reduced motion.
import { useEffect, useState } from "react";

export const reducedMotion = () => window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;

// Elements matching these selectors fade/slide in the first time they scroll into view.
// Siblings get a small stagger so rows of cards "assemble" one after another.
const REVEAL = [
  ".section h2", ".section > .container > p", ".card", ".gallery-item", ".step", ".hours-counter",
  ".carousel", ".cta h2", ".cta .actions", ".marquee",
].join(",");

export function useAutoReveal() {
  useEffect(() => {
    if (reducedMotion() || !("IntersectionObserver" in window)) return;
    const seen = new WeakSet();
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (!e.isIntersecting) return;
        e.target.classList.add("revealed");
        io.unobserve(e.target);
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });

    const scan = () => {
      document.querySelectorAll(REVEAL).forEach((el) => {
        if (seen.has(el) || el.closest(".lightbox, .header, .contact-fab, .hero, .carousel-track")) return;
        seen.add(el);
        const siblings = [...el.parentElement.children].filter((c) => c.matches(REVEAL));
        el.style.setProperty("--reveal-delay", `${Math.min(siblings.indexOf(el), 6) * 90}ms`);
        el.classList.add("reveal");
        io.observe(el);
      });
    };
    scan();
    // Content arrives from the API after the first render, so keep watching for new elements.
    const mo = new MutationObserver(scan);
    mo.observe(document.getElementById("root"), { childList: true, subtree: true });
    return () => { io.disconnect(); mo.disconnect(); };
  }, []);
}

/** Scroll progress 0..1 and whether the page has scrolled at all. */
export function useScroll() {
  const [state, setState] = useState({ progress: 0, scrolled: false, y: 0 });
  useEffect(() => {
    let frame = 0;
    const update = () => {
      frame = 0;
      const max = document.documentElement.scrollHeight - window.innerHeight;
      setState({ progress: max > 0 ? window.scrollY / max : 0, scrolled: window.scrollY > 10, y: window.scrollY });
    };
    const onScroll = () => { if (!frame) frame = requestAnimationFrame(update); };
    update();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    return () => { window.removeEventListener("scroll", onScroll); window.removeEventListener("resize", onScroll); cancelAnimationFrame(frame); };
  }, []);
  return state;
}
