// Photo gallery loaded page by page from /api/gallery/ ("Show more"), with a full-screen lightbox.
import { useCallback, useEffect, useState } from "react";
import { useI18n } from "../i18n.jsx";
import Lightbox from "./Lightbox.jsx";

export default function Gallery({ total, children }) {
  const { t } = useI18n();
  const [images, setImages] = useState([]);
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(null);

  const loadMore = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`/api/gallery/?page=${page + 1}`);
      const data = await res.json();
      setImages((cur) => [...cur, ...data.results]);
      setPage((p) => p + 1);
      setHasMore(Boolean(data.next));
    } catch {
      setHasMore(false);
    } finally {
      setLoading(false);
    }
  }, [page]);

  useEffect(() => { loadMore(); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  if (!images.length && !loading) return null;
  return (
    <>
      <div className="gallery">
        {images.map((img, i) => (
          <button key={img.id} className="gallery-item" onClick={() => setOpen(i)} aria-label={img.caption || t("ui.open")}>
            <img src={img.src} alt={img.caption} loading="lazy" />
          </button>
        ))}
      </div>
      <div className="actions center">
        {hasMore && (
          <button className="btn btn-ghost" onClick={loadMore} disabled={loading}>
            {t("ui.showMore")} ({images.length} / {total})
          </button>
        )}
        {children}
      </div>
      {open !== null && <Lightbox images={images} index={open} onChange={setOpen} onClose={() => setOpen(null)} />}
    </>
  );
}
