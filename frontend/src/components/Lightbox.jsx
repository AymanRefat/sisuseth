// Full-screen photo viewer: arrows, keyboard (← → Esc) and swipe.
import { useEffect, useRef } from "react";
import { useI18n } from "../i18n.jsx";

export default function Lightbox({ images, index, onChange, onClose }) {
  const { t } = useI18n();
  const touchX = useRef(null);
  const image = images[index];
  const go = (step) => onChange((index + step + images.length) % images.length);

  useEffect(() => {
    const onKey = (e) => {
      if (e.key === "Escape") onClose();
      if (e.key === "ArrowRight") onChange((index + 1) % images.length);
      if (e.key === "ArrowLeft") onChange((index - 1 + images.length) % images.length);
    };
    document.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [index, images.length, onChange, onClose]);

  if (!image) return null;
  return (
    <div className="lightbox" role="dialog" aria-modal="true" onClick={onClose}
         onTouchStart={(e) => { touchX.current = e.touches[0].clientX; }}
         onTouchEnd={(e) => {
           const dx = e.changedTouches[0].clientX - (touchX.current ?? 0);
           if (Math.abs(dx) > 50) go(dx < 0 ? 1 : -1);
         }}>
      <img src={image.src} alt={image.caption} onClick={(e) => e.stopPropagation()} />
      {image.caption && <p className="lightbox-caption">{image.caption}</p>}
      <span className="lightbox-count">{index + 1} / {images.length}</span>
      <button className="lightbox-close" onClick={onClose} aria-label={t("ui.close")}>×</button>
      {images.length > 1 && <>
        <button className="lightbox-arrow prev" onClick={(e) => { e.stopPropagation(); go(-1); }} aria-label={t("ui.previous")}>‹</button>
        <button className="lightbox-arrow next" onClick={(e) => { e.stopPropagation(); go(1); }} aria-label={t("ui.next")}>›</button>
      </>}
    </div>
  );
}
