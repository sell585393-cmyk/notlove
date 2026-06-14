import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import { HomePage } from "./pages/HomePage";
import { initTelegramApp } from "./lib/telegram";

// Инициализируем Telegram Web App
initTelegramApp();

const rootEl = document.getElementById("root");
if (rootEl) {
  createRoot(rootEl).render(
    <StrictMode>
      <HomePage />
    </StrictMode>,
  );
}
