// Feature: videos. Horizontal strip of short, muted, looping clips.
import { useI18n } from "../i18n.jsx";

export default function VideoStrip({ videos }) {
  const { t } = useI18n();
  if (!videos.length) return null;
  return (
    <section className="section alt">
      <div className="container">
        <h2 className="center">{t("videos.title")}</h2>
        <p className="center muted">{t("videos.subtitle")}</p>
        <div className="video-strip">
          {videos.map((v) => (
            <figure key={v.id}>
              <video src={v.src} poster={v.poster || undefined} autoPlay muted loop playsInline preload="metadata" />
              {v.caption && <figcaption>{v.caption}</figcaption>}
            </figure>
          ))}
        </div>
      </div>
    </section>
  );
}
