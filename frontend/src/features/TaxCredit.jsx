// Feature: tax_credit. Kotitalousvähennys estimate: credit = price × labour share × rate.
import { useEffect, useState } from "react";
import { useI18n } from "../i18n.jsx";

export default function TaxCredit({ rules, defaultPrice }) {
  const { t } = useI18n();
  const [price, setPrice] = useState(defaultPrice);
  useEffect(() => setPrice(defaultPrice), [defaultPrice]);

  const credit = Math.min(rules.max, (Number(price) || 0) * (rules.labour / 100) * (rules.rate / 100));
  const effective = Math.max(0, (Number(price) || 0) - credit);
  const eur = (n) => `€${n.toFixed(2).replace(/\.00$/, "")}`;

  return (
    <div className="card tax">
      <h3>🧾 {t("tax.title")}</h3>
      <p className="muted">{t("tax.subtitle")}</p>
      <label>{t("tax.price")}
        <input type="number" min="0" step="5" value={price} onChange={(e) => setPrice(e.target.value)} />
      </label>
      <div className="tax-row"><span>{t("tax.credit", { rate: rules.rate })}</span><strong>−{eur(credit)}</strong></div>
      <div className="tax-row total"><span>{t("tax.effective")}</span><strong>{eur(effective)}</strong></div>
      <p className="muted small">{t("tax.note", { deductible: rules.deductible, max: rules.max })}</p>
    </div>
  );
}
