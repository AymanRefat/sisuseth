import { createContext, useCallback, useContext, useEffect, useState } from "react";
import en from "./locales/en.json";
import fi from "./locales/fi.json";
import sv from "./locales/sv.json";

export const LANGUAGES = { fi: "FI", sv: "SV", en: "EN" };
const BUNDLED = { en, fi, sv };

function initialLang() {
  try {
    const saved = localStorage.getItem("lang");
    if (saved in BUNDLED) return saved;
  } catch { /* storage unavailable */ }
  return "fi"; // Finnish by default; visitors can switch and the choice is remembered.
}

const I18nContext = createContext(null);

export function I18nProvider({ children }) {
  const [lang, setLangState] = useState(initialLang);
  const [content, setContent] = useState(null);

  useEffect(() => {
    document.documentElement.lang = lang;
    let cancelled = false;
    fetch(`/api/content/?lang=${lang}`)
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then((data) => !cancelled && setContent(data))
      .catch(() => !cancelled && setContent((c) => c ?? { texts: {} }));
    return () => { cancelled = true; };
  }, [lang]);

  const setLang = (next) => {
    setLangState(next);
    try { localStorage.setItem("lang", next); } catch { /* ignore */ }
  };

  // CMS override → bundled language → English → the key itself.
  const t = useCallback((key, vars = {}) => {
    const text = content?.texts?.[key] ?? BUNDLED[lang][key] ?? fi[key] ?? key;
    return text.replace(/\{(\w+)\}/g, (_, v) => (v in vars ? vars[v] : `{${v}}`));
  }, [content, lang]);

  return <I18nContext.Provider value={{ lang, setLang, t, content }}>{children}</I18nContext.Provider>;
}

export const useI18n = () => useContext(I18nContext);
