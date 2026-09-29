// Feature: product_search. Type "PAX" → price and time for that product.
import { useState } from "react";
import { useI18n } from "../i18n.jsx";
import { formatMinutes } from "./utils.js";

export default function ProductSearch({ products, BookButtons, settings }) {
  const { t } = useI18n();
  const [query, setQuery] = useState("");
  const q = query.trim().toLowerCase();
  const results = q ? products.filter((p) => `${p.brand} ${p.name}`.toLowerCase().includes(q)).slice(0, 6) : [];

  return (
    <div className="card search">
      <h3>🔎 {t("search.title")}</h3>
      <p className="muted">{t("search.subtitle")}</p>
      <input type="search" value={query} placeholder={t("search.placeholder")} onChange={(e) => setQuery(e.target.value)} />
      {q && results.length === 0 && <p className="muted">{t("search.empty")}</p>}
      <ul className="search-results">
        {results.map((p) => (
          <li key={p.id}>
            <div>
              <strong>{p.brand} {p.name}</strong>
              <span className="muted"> · {t("search.time", { time: formatMinutes(p.minutes) })}</span>
            </div>
            <div className="search-price">€{p.price}</div>
            <BookButtons s={settings} compact label={t("search.book")}
                         text={t("wa.product", { brand: p.brand, name: p.name, price: p.price })} />
          </li>
        ))}
      </ul>
    </div>
  );
}
