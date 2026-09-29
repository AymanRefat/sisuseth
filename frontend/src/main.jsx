import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.jsx";
import { I18nProvider } from "./i18n.jsx";
import { ReferralProvider } from "./features/referral.jsx";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <I18nProvider>
      <ReferralProvider>
        <App />
      </ReferralProvider>
    </I18nProvider>
  </StrictMode>,
);
