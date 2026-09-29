// Feature: quiz. "How long would it take you?" – DIY time = our time × skill multiplier.
import { useState } from "react";
import { useI18n } from "../i18n.jsx";
import { formatMinutes } from "./utils.js";

const SKILLS = ["beginner", "average", "handy"];

export default function Quiz({ products, multipliers, BookButtons, settings }) {
  const { t } = useI18n();
  const [productId, setProductId] = useState(null);
  const [skill, setSkill] = useState(null);
  if (!products.length) return null;
  const product = products.find((p) => p.id === productId) ?? products[0];
  const diyMinutes = skill ? product.minutes * multipliers[skill] : 0;
  const argumentsCount = Math.max(1, Math.round(diyMinutes / 60));

  return (
    <section className="section">
      <div className="container narrow">
        <div className="card quiz">
          <h2 className="center">🤔 {t("quiz.title")}</h2>
          <p className="center muted">{t("quiz.subtitle")}</p>
          <label>{t("quiz.item")}
            <select value={product.id} onChange={(e) => setProductId(Number(e.target.value))}>
              {products.map((p) => <option key={p.id} value={p.id}>{p.brand} {p.name}</option>)}
            </select>
          </label>
          <p><strong>{t("quiz.skill")}</strong></p>
          <div className="quiz-skills">
            {SKILLS.map((s) => (
              <button key={s} className={`chip ${skill === s ? "active" : ""}`} onClick={() => setSkill(s)}>{t(`quiz.${s}`)}</button>
            ))}
          </div>
          {skill && (
            <div className="quiz-result" key={`${product.id}-${skill}`}>
              <p className="quiz-diy">😩 {t("quiz.diy", { time: formatMinutes(diyMinutes) })}</p>
              <p className="muted">{t("quiz.args", { n: argumentsCount })}</p>
              <p className="quiz-us">😎 {t("quiz.us", { time: formatMinutes(product.minutes), price: product.price })}</p>
              <BookButtons s={settings} label={t("quiz.cta")}
                           text={t("wa.product", { brand: product.brand, name: product.name, price: product.price })} />
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
