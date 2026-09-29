// Feature: mobile_bar. Always-visible booking buttons at the bottom of phone screens.
import { useI18n } from "../i18n.jsx";

export default function MobileBar({ settings, whatsapp, telegram }) {
  const { t } = useI18n();
  return (
    <div className="mobile-bar">
      <a href={whatsapp} target="_blank" rel="noreferrer" className="mb-wa">WhatsApp</a>
      {settings.telegram && <a href={telegram} target="_blank" rel="noreferrer" className="mb-tg">Telegram</a>}
      <a href={`tel:${settings.phone.replace(/\s/g, "")}`} className="mb-call">📞 {t("bar.call")}</a>
    </div>
  );
}
