// Feature: referrals. Captures ?ref=CODE from the URL, validates it and remembers it,
// so booking buttons and the booking form include the code automatically.
import { createContext, useContext, useEffect, useState } from "react";
import { useI18n } from "../i18n.jsx";
import { safeStorage } from "./utils.js";

const ReferralContext = createContext({ code: "", setCode: () => {} });

export function ReferralProvider({ children }) {
  const [code, setCode] = useState(() => safeStorage.get("ref") || "");

  useEffect(() => {
    const fromUrl = new URLSearchParams(window.location.search).get("ref");
    if (!fromUrl) return;
    fetch(`/api/referrals/${encodeURIComponent(fromUrl)}/`)
      .then((r) => r.json())
      .then(({ valid }) => {
        if (!valid) return;
        const upper = fromUrl.toUpperCase();
        setCode(upper);
        safeStorage.set("ref", upper);
      })
      .catch(() => {});
  }, []);

  return <ReferralContext.Provider value={{ code, setCode }}>{children}</ReferralContext.Provider>;
}

export const useReferral = () => useContext(ReferralContext);

export function ReferralBanner({ discount }) {
  const { t } = useI18n();
  const { code } = useReferral();
  if (!code) return null;
  return <div className="ref-banner">🎁 {t("ref.applied", { code, discount })}</div>;
}

export function ReferralSection({ discount, whatsappShare }) {
  const { t } = useI18n();
  const [myCode, setMyCode] = useState(() => safeStorage.get("myRef") || "");
  const [status, setStatus] = useState("idle");
  const [copied, setCopied] = useState(false);
  const link = myCode ? `${window.location.origin}/?ref=${myCode}` : "";

  const submit = async (e) => {
    e.preventDefault();
    setStatus("sending");
    try {
      const res = await fetch("/api/referrals/", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(Object.fromEntries(new FormData(e.target))),
      });
      if (!res.ok) throw new Error(res.status);
      const { code } = await res.json();
      setMyCode(code);
      safeStorage.set("myRef", code);
      setStatus("idle");
    } catch {
      setStatus("error");
    }
  };

  const copy = async () => {
    try { await navigator.clipboard.writeText(link); setCopied(true); } catch { /* clipboard blocked */ }
  };

  return (
    <section className="section">
      <div className="container narrow center">
        <h2>🎁 {t("ref.title")}</h2>
        <p className="muted">{t("ref.subtitle", { discount })}</p>
        {myCode ? (
          <div className="card ref-result">
            <p>{t("ref.yours")}</p>
            <div className="ref-code">{myCode}</div>
            <p className="muted ref-link">{link}</p>
            <div className="actions center">
              <button className="btn btn-ghost" onClick={copy}>{copied ? t("ref.copied") : t("ref.copy")}</button>
              <a className="btn btn-wa" target="_blank" rel="noreferrer"
                 href={whatsappShare(t("ref.shareText", { discount, url: link }))}>{t("ref.share")}</a>
            </div>
          </div>
        ) : (
          <form className="card form" onSubmit={submit}>
            <label>{t("ref.name")}<input name="name" required maxLength={100} /></label>
            <label>{t("ref.phone")}<input name="phone" type="tel" required maxLength={30} /></label>
            {status === "error" && <p className="error full">{t("ref.error")}</p>}
            <button className="btn full" disabled={status === "sending"}>{t("ref.get")}</button>
          </form>
        )}
      </div>
    </section>
  );
}
