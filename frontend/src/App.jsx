import { useEffect, useState } from "react";
import { LANGUAGES, useI18n } from "./i18n.jsx";
import BeforeAfter from "./features/BeforeAfter.jsx";
import HeroAnimation from "./features/HeroAnimation.jsx";
import HoursCounter from "./features/HoursCounter.jsx";
import ContactFab from "./features/ContactFab.jsx";
import ProductSearch from "./features/ProductSearch.jsx";
import Quiz from "./features/Quiz.jsx";
import TaxCredit from "./features/TaxCredit.jsx";
import VideoStrip from "./features/VideoStrip.jsx";
import { useInView } from "./features/utils.js";
import Carousel from "./components/Carousel.jsx";
import ScrollTape from "./components/ScrollTape.jsx";
import { Chair, Lamp, Plant, Screw, Scribble, Shelf } from "./components/Illustrations.jsx";
import { useAutoReveal, useScroll } from "./components/motion.js";
import PhotoGallery from "./components/Gallery.jsx";

const DEFAULT_SETTINGS = {
  phone: "+358 40 871 3636", whatsapp: "358408713636", email: "info@sisuseth.com",
  areas: ["Helsinki", "Espoo", "Vantaa"], happyCustomers: 500, startingPrice: 50, hourlyRate: 40,
  additionalItem: 45, brands: ["IKEA", "JYSK", "Sotka", "ISKU", "Treetale", "Kodin1"], logo: "", heroImage: "",
  // Optional features (docs/FEATURES.md). All off until the CMS says otherwise.
  features: {}, hoursSaved: 0, quiz: { beginner: 4, average: 2.5, handy: 1.5 },
  taxCredit: { rate: 35, labour: 100, deductible: 150, max: 1600 },
};

const waLink = (number, text) => `https://wa.me/${number}?text=${encodeURIComponent(text)}`;
// Telegram prefills the message on recent apps; older ones just open the chat.
const tgLink = (username, text) => `https://t.me/${username}?text=${encodeURIComponent(text)}`;

function BookButtons({ s, text, label, compact = false }) {
  const { t } = useI18n();
  const message = text ?? t("wa.default");
  const cls = compact ? "btn btn-sm" : "btn";
  return (
    <span className="book-buttons">
      <a className={`${cls} btn-wa`} href={waLink(s.whatsapp, message)} target="_blank" rel="noreferrer">
        {compact ? "WhatsApp" : label}
      </a>
      {s.telegram && (
        <a className={`${cls} btn-tg`} href={tgLink(s.telegram, message)} target="_blank" rel="noreferrer">Telegram</a>
      )}
    </span>
  );
}

export default function App() {
  const { t, content } = useI18n();
  const s = { ...DEFAULT_SETTINGS, ...content?.settings };
  const areas = s.areas.join(", ");
  const f = s.features;
  useAutoReveal();

  // The logo doubles as the favicon, so a new logo in the CMS updates the browser tab icon too.
  useEffect(() => {
    if (!s.logo) return;
    document.querySelectorAll("link[rel='icon'], link[rel='apple-touch-icon']").forEach((l) => { l.href = s.logo; });
  }, [s.logo]);

  return (
    <>
      <Header s={s} />
      <main>
        <Hero s={s} areas={areas} showBoxAnimation={f.hero_animation} />

        <Pains items={content?.pains ?? []} />
        <Gallery total={content?.galleryCount ?? 0} s={s} areas={areas} />
        {f.before_after && <BeforeAfter items={content?.beforeAfter ?? []} />}
        {f.videos && <VideoStrip videos={content?.videos ?? []} />}
        <Steps items={content?.steps ?? []}>{f.hours_counter && <HoursCounter hours={s.hoursSaved} areas={areas} />}</Steps>
        <Compare rows={content?.timeline ?? []} animate={f.timeline_animation} />
        {f.quiz && <Quiz products={content?.products ?? []} multipliers={s.quiz} BookButtons={BookButtons} settings={s} />}
        <Reviews items={content?.testimonials ?? []} count={s.happyCustomers} brands={s.brands} />
        <Pricing content={content} settings={s} />
        <Faq items={content?.faq ?? []} />
        <BookingForm />

        <section className="cta">
          <Chair className="cta-deco cta-chair" />
          <Shelf className="cta-deco cta-shelf" />
          <div className="container center">
            <h2>{t("cta.title")}</h2>
            <p>{t("cta.subtitle")}</p>
            <div className="actions center">
              <BookButtons s={s} label={t("cta.whatsapp")} />
              <a className="btn btn-ghost" href={`tel:${s.phone.replace(/\s/g, "")}`}>{t("cta.call")}</a>
            </div>
            <p className="muted">{t("cta.perks")}</p>
          </div>
        </section>
      </main>
      <Footer s={s} />
      {f.mobile_bar && (
        <ContactFab settings={s} whatsapp={waLink(s.whatsapp, t("wa.default"))} telegram={tgLink(s.telegram, t("wa.default"))} />
      )}
    </>
  );
}

/** Renders "Don't waste your *weekend*!" word by word; the *starred* word gets a drawn underline. */
function AnimatedTitle({ text }) {
  let i = 0;
  return (
    <h1 className="hero-title">
      {text.split(/(\*[^*]+\*)/).filter(Boolean).map((part) => {
        const highlight = part.startsWith("*") && part.endsWith("*");
        return (highlight ? [part.slice(1, -1)] : part.split(/(\s+)/)).map((word) => {
          if (/^\s+$/.test(word)) return word;
          const style = { "--i": i++ };
          return highlight
            ? <span key={i} className="word highlight" style={style}>{word}<Scribble /></span>
            : <span key={i} className="word" style={style}>{word}</span>;
        });
      })}
    </h1>
  );
}

function Hero({ s, areas, showBoxAnimation }) {
  const { t } = useI18n();
  const { y } = useScroll();
  const drift = Math.min(y, 600);
  return (
    <section className="hero">
      <div className="hero-blueprint" aria-hidden="true" />
      <Lamp className="hero-lamp" />
      <div className="container hero-grid">
        <div className="hero-copy">
          <p className="eyebrow"><span className="eyebrow-dot" />{t("hero.eyebrow")}</p>
          <AnimatedTitle text={t("hero.title")} />
          <p className="lead">{t("hero.subtitle", { areas })}</p>
          <div className="actions">
            <BookButtons s={s} label={t("hero.cta")} />
            <a className="btn btn-ghost" href="#gallery">{t("hero.secondary")}</a>
          </div>
          <div className="badges">
            <span>⭐ {t("hero.badge", { count: s.happyCustomers })}</span>
            <span>💶 {t("hero.from", { price: s.startingPrice })}</span>
          </div>
        </div>
        <div className="hero-visual">
          <div className="hero-frame" style={{ transform: `translateY(${drift * -0.06}px)` }}>
            {s.heroImage && <img className="hero-img" src={s.heroImage} alt="" />}
          </div>
          <Plant className="hero-plant" style={{ transform: `translateY(${drift * -0.15}px)` }} />
          <div className="float-card float-card-a">⚡ {t("hero.floatA")}</div>
          <div className="float-card float-card-b">🛡️ {t("hero.floatB")}</div>
          {showBoxAnimation && <HeroAnimation />}
        </div>
      </div>
      <a href="#services" className="scroll-cue" aria-label={t("nav.services")}><span /></a>
    </section>
  );
}

function Header({ s }) {
  const { t, lang, setLang } = useI18n();
  const { scrolled } = useScroll();
  return (
    <header className={`header ${scrolled ? "scrolled" : ""}`}>
      <ScrollTape />
      <div className="container header-row">
        <a href="#" className="logo">{s.logo ? <img src={s.logo} alt="SISUSETH" /> : "SISUSETH"}</a>
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
          <BookButtons s={s} label={t("nav.book")} compact />
        </div>
      </div>
    </header>
  );
}

function Pains({ items }) {
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
          {items.map((p) => (
            <button key={p.id} className={`card pain ${picked.includes(p.id) ? "picked" : ""}`}
                    onClick={() => toggle(p.id)} aria-pressed={picked.includes(p.id)}>
              <span className="pain-icon">{p.icon || "🪛"}</span>
              <strong>{p.title}</strong>
              <span>{p.text}</span>
              <span className="pain-stamp" aria-hidden="true">✓</span>
            </button>
          ))}
        </div>
        {picked.length > 0 && <p className="center pain-result" key={picked.length}>🛠️ {t("pain.result", { n: picked.length })}</p>}
      </div>
    </section>
  );
}

function Gallery({ total, s, areas }) {
  const { t } = useI18n();
  return (
    <section id="gallery" className="section alt">
      <div className="container">
        <h2 className="center">{t("gallery.title")}</h2>
        <p className="center muted">{t("gallery.subtitle", { areas })}</p>
        <PhotoGallery total={total}>
          <BookButtons s={s} label={t("gallery.cta")} />
        </PhotoGallery>
      </div>
    </section>
  );
}

function Steps({ items, children }) {
  const { t } = useI18n();
  return (
    <section className="section">
      <div className="container">
        <h2 className="center">{t("steps.title")}</h2>
        <p className="center muted">{t("steps.subtitle")}</p>
        <ol className="steps">
          {items.map((step, i) => (
            <li key={step.id} className="step">
              <div className="step-num"><Screw /><span>{i + 1}</span></div>
              <h3>{step.title}</h3>
              <p>{step.text}</p>
            </li>
          ))}
        </ol>
        {children}
      </div>
    </section>
  );
}

function Compare({ rows, animate }) {
  const { t } = useI18n();
  const [ref, inView] = useInView();
  const col = (key, icon, cls) => (
    <div className={`card compare ${cls} ${animate ? "animated" : ""} ${animate && inView ? "play" : ""}`}>
      <h3>{icon} {t(`compare.${key}`)}</h3>
      <ul>
        {rows.filter((r) => r.side === key).map((r) => <li key={r.id}><b>{r.time}</b> {r.text}</li>)}
      </ul>
    </div>
  );
  return (
    <section className="section alt" ref={ref}>
      <div className="container">
        <h2 className="center">{t("compare.title")}</h2>
        <div className="grid grid-2">
          {col("diy", "❌", "bad")}
          {col("us", "✅", "good")}
        </div>
      </div>
    </section>
  );
}

function Reviews({ items, count, brands }) {
  const { t } = useI18n();
  return (
    <section id="reviews" className="section">
      <div className="container">
        <h2 className="center">{t("reviews.title", { count })}</h2>
        <p className="center muted">{t("reviews.subtitle")}</p>
        <Carousel className="reviews" autoPlayMs={7000} label={t("reviews.title", { count })}>
          {items.map((r) => (
            <figure key={r.id} className="card review">
              <blockquote>“{r.quote}”</blockquote>
              <figcaption><strong>{r.author}</strong> · {r.city}</figcaption>
            </figure>
          ))}
        </Carousel>
        <p className="center muted brands-title">{t("brands.title")}</p>
        <div className="marquee" aria-label={brands.join(", ")}>
          <div className="marquee-track">
            {[...brands, ...brands].map((b, i) => <span key={i} aria-hidden={i >= brands.length}>{b}</span>)}
          </div>
        </div>
      </div>
    </section>
  );
}

function Pricing({ content, settings }) {
  const { t } = useI18n();
  const options = content?.calculator ?? [];
  const [optionId, setOptionId] = useState(null);
  const [qty, setQty] = useState(1);
  const option = options.find((o) => o.id === optionId) ?? options[0];
  const estimateEur = option && !option.hourly ? option.price + (qty - 1) * settings.additionalItem : option?.price ?? 0;
  const estimate = option
    ? option.hourly ? `€${option.price}${t("calc.hourly")}` : `€${option.price + (qty - 1) * settings.additionalItem}`
    : "";

  return (
    <section id="pricing" className="section alt">
      <div className="container">
        <h2 className="center">{t("pricing.title")}</h2>
        <p className="center muted">{t("pricing.subtitle", { price: settings.startingPrice, hourly: settings.hourlyRate })}</p>

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
              <BookButtons s={settings} text={t("wa.package", { name: p.name, price: p.price })} label={t("pricing.book", { name: p.name })} />
            </div>
          ))}
        </div>
        {settings.features.product_search && (content?.products ?? []).length > 0 && (
          <ProductSearch products={content.products} BookButtons={BookButtons} settings={settings} />
        )}

        <div className="pricing-tools">
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
                <small className="muted">{t("calc.extra")}: €{settings.additionalItem}</small>
              </label>
            )}
            <div className="calc-total">{estimate}</div>
            <p className="muted">{t("calc.includes")}</p>
            <BookButtons s={settings} text={t("wa.estimate", { price: estimate })} label={t("calc.book")} />
          </div>
        )}

        {settings.features.tax_credit && <TaxCredit rules={settings.taxCredit} defaultPrice={estimateEur} />}

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
    // Drop empty optional fields (e.g. no date picked) so the API doesn't reject them.
    const data = Object.fromEntries([...new FormData(e.target)].filter(([, v]) => v !== ""));
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
          <p className="footer-social">{socials.map(([name, url]) => <a key={name} href={url} target="_blank" rel="noreferrer">{name}</a>)}</p>
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
