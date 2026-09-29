// Feature: mobile_bar (shown in the CMS as "Floating contact button").
// One round button in the bottom-right corner; tapping it pops up WhatsApp / Telegram / Call.
import { useEffect, useRef, useState } from "react";
import { useI18n } from "../i18n.jsx";

const Icon = {
  chat: <path d="M4 5h16v11H8l-4 4z" />,
  close: <path d="M6 6l12 12M18 6L6 18" />,
  whatsapp: <path d="M12 3a9 9 0 0 0-7.8 13.5L3 21l4.6-1.2A9 9 0 1 0 12 3zm-3 5c.3 0 .6 0 .8.5l.9 2c.1.3 0 .5-.2.7l-.6.7c.6 1.2 1.6 2.2 2.9 2.9l.7-.7c.2-.2.5-.3.7-.2l2 .9c.4.2.5.5.4.9-.3 1.1-1.3 1.9-2.4 1.8C11 17 7 13 7 9.9 7 8.8 7.9 8 9 8z" />,
  telegram: <path d="M21 4L3 11l6 2 2 6 3-4 5 4zM9 13l9-7-7 9" />,
  phone: <path d="M6 3h3l2 5-2.5 1.5a11 11 0 0 0 5 5L15 12l5 2v3a2 2 0 0 1-2 2A16 16 0 0 1 4 5a2 2 0 0 1 2-2z" />,
};
const Svg = ({ name }) => (
  <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    {Icon[name]}
  </svg>
);

export default function ContactFab({ settings, whatsapp, telegram }) {
  const { t } = useI18n();
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    if (!open) return;
    const onKey = (e) => e.key === "Escape" && setOpen(false);
    const onClick = (e) => !ref.current?.contains(e.target) && setOpen(false);
    document.addEventListener("keydown", onKey);
    document.addEventListener("pointerdown", onClick);
    return () => { document.removeEventListener("keydown", onKey); document.removeEventListener("pointerdown", onClick); };
  }, [open]);

  const options = [
    { key: "wa", icon: "whatsapp", label: "WhatsApp", href: whatsapp, external: true },
    settings.telegram && { key: "tg", icon: "telegram", label: "Telegram", href: telegram, external: true },
    { key: "call", icon: "phone", label: `${t("bar.call")} ${settings.phone}`, href: `tel:${settings.phone.replace(/\s/g, "")}` },
  ].filter(Boolean);

  return (
    <div className={`contact-fab ${open ? "open" : ""}`} ref={ref}>
      <ul className="fab-menu" id="fab-menu" aria-hidden={!open}>
        {options.map((o, i) => (
          <li key={o.key} style={{ "--i": options.length - 1 - i }}>
            <a className={`fab-option fab-${o.key}`} href={o.href} tabIndex={open ? 0 : -1} onClick={() => setOpen(false)}
               {...(o.external ? { target: "_blank", rel: "noreferrer" } : {})}>
              <span className="fab-label">{o.label}</span>
              <span className="fab-icon"><Svg name={o.icon} /></span>
            </a>
          </li>
        ))}
      </ul>
      <button className="fab-main" onClick={() => setOpen((v) => !v)} aria-expanded={open} aria-controls="fab-menu"
              aria-label={open ? t("ui.close") : t("fab.open")}>
        <span className="fab-main-icon chat"><Svg name="chat" /></span>
        <span className="fab-main-icon close"><Svg name="close" /></span>
      </button>
      {!open && <span className="fab-hint" aria-hidden="true">{t("fab.hint")}</span>}
    </div>
  );
}
