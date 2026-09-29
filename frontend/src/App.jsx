import { useState } from "react";
import { LANGUAGES, useI18n } from "./i18n.jsx";

const DEFAULT_SETTINGS = {
  phone: "+358 40 871 3636", whatsapp: "358408713636", email: "info@sisuseth.com",
  areas: ["Helsinki", "Espoo", "Vantaa"], happyCustomers: 500, startingPrice: 50, hourlyRate: 40,
};
const PAINS = ["tools", "time", "instructions", "damage", "space", "stress"];
const BRANDS = ["IKEA", "JYSK", "Sotka", "ISKU", "Treetale", "Kodin1"];
const ADDITIONAL_ITEM_EUR = 45;

const waLink = (number, text) => `https://wa.me/${number}?text=${encodeURIComponent(text)}`;

export default function App() {
  const { t, content } = useI18n();
  const s = { ...DEFAULT_SETTINGS, ...content?.settings };
  const areas = s.areas.join(", ");
  const wa = (text = t("wa.default")) => waLink(s.whatsapp, text);

  return (
    <>
      <Header wa={wa} />
      <main>
        <section className="hero">
          <div className="container">
            <p className="eyebrow">{t("hero.eyebrow")}</p>
            <h1>{t("hero.title")}</h1>
            <p className="lead">{t("hero.subtitle", { areas })}</p>
            <div className="actions">
              <a className="btn" href={wa()} target="_blank" rel="noreferrer">{t("hero.cta")}</a>
              <a className="btn btn-ghost" href="#gallery">{t("hero.secondary")}</a>
            </div>
            <div className="badges">
              <span>⭐ {t("hero.badge", { count: s.happyCustomers })}</span>
              <span>💶 {t("hero.from", { price: s.startingPrice })}</span>
            </div>
          </div>
        </section>

        <Pains />
        <Gallery images={content?.gallery ?? []} wa={wa} areas={areas} />
        <Steps />
        <Compare />
        <Reviews items={content?.testimonials ?? []} count={s.happyCustomers} />
        <Pricing content={content} settings={s} wa={wa} />
        <Faq items={content?.faq ?? []} />
        <BookingForm />

        <section className="cta">
          <div className="container center">
            <h2>{t("cta.title")}</h2>
            <p>{t("cta.subtitle")}</p>
            <div className="actions center">
              <a className="btn" href={wa()} target="_blank" rel="noreferrer">{t("cta.whatsapp")}</a>
              <a className="btn btn-ghost" href={`tel:${s.phone.replace(/\s/g, "")}`}>{t("cta.call")}</a>
            </div>
            <p className="muted">{t("cta.perks")}</p>
          </div>
        </section>
      </main>
      <Footer s={s} />
    </>
  );
}

function Header({ wa }) {
  const { t, lang, setLang } = useI18n();
  return (
    <header className="header">
      <div className="container header-row">
        <a href="#" className="logo">SISUSETH</a>
        <nav>
          <a href="#services">{t("nav.services")}</a>
          <a href="#reviews">{t("nav.reviews")}</a>
          <a href="#pricing">{t("nav.pricing")}</a>
          <a href="#contact">{t("nav.contact")}</a>
        </nav>
        <div className="header-right">
          <div className="lang-switch" role="group" aria-label="Language">
            {Object.entries(LANGUAGES).map(([code, label]) => (
              <button key={code} className={code === lang ? "active" : ""} onClick={() => setLang(code)}>{label}</button>
            ))}
          </div>
          <a className="btn btn-sm" href={wa()} target="_blank" rel="noreferrer">{t("nav.book")}</a>
        </div>
      </div>
    </header>
  );
}

function Pains() {
  const { t } = useI18n();
  const [picked, setPicked] = useState([]);
  const toggle = (p) => setPicked((cur) => (cur.includes(p) ? cur.filter((x) => x !== p) : [...cur, p]));
  return (
    <section id="services" className="section">
      <div className="container">
        <h2 className="center">{t("pain.title")}</h2>
        <p className="center muted">{t("pain.subtitle")}</p>
        <p className="center"><strong>{t("pain.pick")}</strong></p>
        <div className="grid grid-3">
          {PAINS.map((p) => (
            <button key={p} className={`card pain ${picked.includes(p) ? "picked" : ""}`} onClick={() => toggle(p)}>
              <strong>{t(`pain.${p}.title`)}</strong>
              <span>{t(`pain.${p}.text`)}</span>
            </button>
          ))}
        </div>
        {picked.length > 0 && <p className="center highlight">{t("pain.result", { n: picked.length })}</p>}
      </div>
    </section>
  );
}

function Gallery({ images, wa, areas }) {
  const { t } = useI18n();
  return (
    <section id="gallery" className="section alt">
      <div className="container">
        <h2 className="center">{t("gallery.title")}</h2>
        <p className="center muted">{t("gallery.subtitle", { areas })}</p>
        <div className="gallery">
          {images.map((img) => <img key={img.id} src={img.src} alt={img.caption} loading="lazy" />)}
        </div>
        <div className="actions center">
          <a className="btn" href={wa()} target="_blank" rel="noreferrer">{t("gallery.cta")}</a>
        </div>
      </div>
    </section>
  );
}

function Steps() {
  const { t } = useI18n();
  return (
    <section className="section">
      <div className="container">
        <h2 className="center">{t("steps.title")}</h2>
        <p className="center muted">{t("steps.subtitle")}</p>
        <div className="grid grid-3">
          {[1, 2, 3].map((n) => (
            <div key={n} className="card">
              <div className="step-num">{n}</div>
              <h3>{t(`steps.${n}.title`)}</h3>
              <p>{t(`steps.${n}.text`)}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Compare() {
  const { t } = useI18n();
  const diyTimes = ["9:00", "10:30", "12:00", "15:00", "18:00"];
  const usTimes = ["9:00", "10:00", "12:00", "14:00", "15:00"];
  const col = (key, times, icon, cls) => (
    <div className={`card compare ${cls}`}>
      <h3>{icon} {t(`compare.${key}`)}</h3>
      <ul>
        {times.map((time, i) => <li key={i}><b>{time}</b> {t(`compare.${key}.${i + 1}`)}</li>)}
      </ul>
    </div>
  );
  return (
    <section className="section alt">
      <div className="container">
        <h2 className="center">{t("compare.title")}</h2>
        <div className="grid grid-2">
          {col("diy", diyTimes, "❌", "bad")}
          {col("us", usTimes, "✅", "good")}
        </div>
      </div>
    </section>
  );
}

function Reviews({ items, count }) {
  const { t } = useI18n();
  return (
    <section id="reviews" className="section">
      <div className="container">
        <h2 className="center">{t("reviews.title", { count })}</h2>
        <p className="center muted">{t("reviews.subtitle")}</p>
        <div className="grid grid-3">
          {items.map((r) => (
            <figure key={r.id} className="card review">
              <blockquote>“{r.quote}”</blockquote>
              <figcaption><strong>{r.author}</strong> · {r.city}</figcaption>
            </figure>
          ))}
        </div>
        <p className="center muted brands">{t("brands.title")} {BRANDS.join(" · ")}</p>
      </div>
    </section>
  );
}

function Pricing({ content, settings, wa }) {
  const { t } = useI18n();
  const options = content?.calculator ?? [];
  const [optionId, setOptionId] = useState(null);
  const [qty, setQty] = useState(1);
  const option = options.find((o) => o.id === optionId) ?? options[0];
  const estimate = option
    ? option.hourly ? `€${option.price}${t("calc.hourly")}` : `€${option.price + (qty - 1) * ADDITIONAL_ITEM_EUR}`
    : "";

  return (
    <section id="pricing" className="section alt">
      <div className="container">
        <h2 className="center">{t("pricing.title")}</h2>
        <p className="center muted">{t("pricing.subtitle", { price: settings.startingPrice, hourly: settings.hourlyRate })}</p>

        {option && (
          <div className="card calc">
            <h3>{t("calc.title")}</h3>
            <label>{t("calc.type")}
              <select value={option.id} onChange={(e) => setOptionId(Number(e.target.value))}>
                {options.map((o) => <option key={o.id} value={o.id}>{o.label}</option>)}
              </select>
            </label>
            {!option.hourly && (
              <label>{t("calc.qty")}: {qty}{qty === 10 ? "+" : ""}
                <input type="range" min="1" max="10" value={qty} onChange={(e) => setQty(Number(e.target.value))} />
                <small className="muted">{t("calc.extra")}: €{ADDITIONAL_ITEM_EUR}</small>
              </label>
            )}
            <div className="calc-total">{estimate}</div>
            <p className="muted">{t("calc.includes")}</p>
            <a className="btn" href={wa(t("wa.estimate", { price: estimate }))} target="_blank" rel="noreferrer">{t("calc.book")}</a>
          </div>
        )}

        <div className="grid grid-3">
          {(content?.packages ?? []).map((p) => (
            <div key={p.id} className={`card package ${p.popular ? "popular" : ""}`}>
              {p.popular && <span className="tag">{t("pricing.popular")}</span>}
              <h3>{p.name}</h3>
              <div className="price">€{p.price}</div>
              <p className="muted">{t("pricing.hours", { h: p.hours })}</p>
              <ul className="checks">
                <li>{p.description}</li>
                <li>{t("pricing.tools")}</li>
                <li>{t("pricing.cleanup")}</li>
                {p.referralBonus > 0 && <li>{t("pricing.referral", { bonus: p.referralBonus })}</li>}
              </ul>
              <a className="btn" href={wa(t("wa.package", { name: p.name, price: p.price }))} target="_blank" rel="noreferrer">
                {t("pricing.book", { name: p.name })}
              </a>
            </div>
          ))}
        </div>
        <p className="center muted">⚠️ {t("pricing.note")}</p>
      </div>
    </section>
  );
}

function Faq({ items }) {
  const { t } = useI18n();
  return (
    <section className="section">
      <div className="container narrow">
        <h2 className="center">{t("faq.title")}</h2>
        {items.map((f) => (
          <details key={f.id} className="faq">
            <summary>{f.q}</summary>
            <p>{f.a}</p>
          </details>
        ))}
      </div>
    </section>
  );
}

function BookingForm() {
  const { t, lang } = useI18n();
  const [status, setStatus] = useState("idle");

  const submit = async (e) => {
    e.preventDefault();
    setStatus("sending");
    const data = Object.fromEntries(new FormData(e.target));
    try {
      const res = await fetch("/api/bookings/", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...data, language: lang }),
      });
      if (!res.ok) throw new Error(res.status);
      setStatus("done");
      e.target.reset();
    } catch {
      setStatus("error");
    }
  };

  return (
    <section id="contact" className="section alt">
      <div className="container narrow">
        <h2 className="center">{t("booking.title")}</h2>
        <p className="center muted">{t("booking.subtitle")}</p>
        {status === "done" ? <p className="center highlight">{t("booking.success")}</p> : (
          <form className="card form" onSubmit={submit}>
            <label>{t("booking.name")}<input name="name" required maxLength={100} /></label>
            <label>{t("booking.phone")}<input name="phone" type="tel" required maxLength={30} /></label>
            <label>{t("booking.city")}<input name="city" maxLength={50} /></label>
            <label>{t("booking.date")}<input name="preferred_date" type="date" /></label>
            <label className="full">{t("booking.furniture")}<textarea name="furniture" required rows={3} /></label>
            {status === "error" && <p className="error full">{t("booking.error")}</p>}
            <button className="btn full" disabled={status === "sending"}>
              {status === "sending" ? t("booking.sending") : t("booking.submit")}
            </button>
          </form>
        )}
      </div>
    </section>
  );
}

function Footer({ s }) {
  const { t } = useI18n();
  const socials = [["Instagram", s.instagram], ["TikTok", s.tiktok], ["Facebook", s.facebook]].filter(([, url]) => url);
  return (
    <footer className="footer">
      <div className="container grid grid-3">
        <div>
          <div className="logo">SISUSETH</div>
          <p>{t("footer.about")}</p>
          <p>{socials.map(([name, url]) => <a key={name} href={url} target="_blank" rel="noreferrer">{name} </a>)}</p>
        </div>
        <div>
          <h4>{t("footer.contact")}</h4>
          <p><a href={`tel:${s.phone.replace(/\s/g, "")}`}>{s.phone}</a></p>
          <p><a href={`mailto:${s.email}`}>{s.email}</a></p>
        </div>
        <div>
          <h4>{t("footer.areas")}</h4>
          {s.areas.map((a) => <p key={a}>✓ {a}</p>)}
        </div>
      </div>
      <p className="container copyright">© {new Date().getFullYear()} SISUSETH. {t("footer.rights")}</p>
    </footer>
  );
}
