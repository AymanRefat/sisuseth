// Feature: google_reviews. Rating and latest reviews from Google, loaded via our backend (cached 6 h).
import { useEffect, useState } from "react";
import { useI18n } from "../i18n.jsx";

export default function GoogleReviews() {
  const { t, lang } = useI18n();
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch(`/api/google-reviews/?lang=${lang}`).then((r) => r.json()).then(setData).catch(() => setData(null));
  }, [lang]);

  if (!data?.enabled) return null;
  return (
    <div className="google-reviews">
      <h3 className="center">{t("google.title")}</h3>
      <p className="center google-score">{t("google.based", { rating: data.rating?.toFixed(1), count: data.count })}</p>
      <div className="grid grid-3">
        {data.reviews.map((r, i) => (
          <figure key={i} className="card review">
            <div className="stars">{"★".repeat(r.rating)}{"☆".repeat(5 - r.rating)}</div>
            <blockquote>{r.text}</blockquote>
            <figcaption>
              {r.photo && <img src={r.photo} alt="" className="avatar" referrerPolicy="no-referrer" />}
              <strong>{r.author}</strong> · <span className="muted">{r.when}</span>
            </figcaption>
          </figure>
        ))}
      </div>
      {data.url && <p className="center"><a href={data.url} target="_blank" rel="noreferrer">{t("google.all")} →</a></p>}
    </div>
  );
}
