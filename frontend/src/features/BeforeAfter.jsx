// Feature: before_after. Drag to compare the boxes with the finished result.
import { useState } from "react";
import { useI18n } from "../i18n.jsx";
import Carousel from "../components/Carousel.jsx";

function Slider({ item }) {
  const { t } = useI18n();
  const [pos, setPos] = useState(50);
  return (
    <figure className="ba">
      <div className="ba-frame">
        <img src={item.after} alt={t("ba.after")} loading="lazy" />
        <img src={item.before} alt={t("ba.before")} loading="lazy" className="ba-before"
             style={{ clipPath: `inset(0 ${100 - pos}% 0 0)` }} />
        <div className="ba-handle" style={{ left: `${pos}%` }} />
        <span className="ba-label left">{t("ba.before")}</span>
        <span className="ba-label right">{t("ba.after")}</span>
        <input type="range" min="0" max="100" value={pos} aria-label={t("ba.subtitle")}
               onChange={(e) => setPos(Number(e.target.value))} />
      </div>
      {item.caption && <figcaption>{item.caption}</figcaption>}
    </figure>
  );
}

export default function BeforeAfter({ items }) {
  const { t } = useI18n();
  if (!items.length) return null;
  return (
    <section className="section">
      <div className="container">
        <h2 className="center">{t("ba.title")}</h2>
        <p className="center muted">{t("ba.subtitle")}</p>
        <Carousel className="before-after" label={t("ba.title")}>{items.map((item) => <Slider key={item.id} item={item} />)}</Carousel>
      </div>
    </section>
  );
}
