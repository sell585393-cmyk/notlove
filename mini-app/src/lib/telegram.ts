/**
 * Работа с Telegram Web App API
 */

declare global {
  interface Window {
    Telegram?: {
      WebApp: TelegramWebApp;
    };
  }
}

interface TelegramWebApp {
  initData: string;
  initDataUnsafe: {
    user?: {
      id: number;
      first_name: string;
      last_name?: string;
      username?: string;
      language_code?: string;
    };
    start_param?: string;
  };
  version: string;
  platform: string;
  colorScheme: "light" | "dark";
  themeParams: Record<string, string>;
  isExpanded: boolean;
  viewportHeight: number;
  viewportStableHeight: number;
  headerColor: string;
  backgroundColor: string;
  ready(): void;
  expand(): void;
  close(): void;
  setHeaderColor(color: string): void;
  setBackgroundColor(color: string): void;
  enableClosingConfirmation(): void;
  disableClosingConfirmation(): void;
  MainButton: {
    text: string;
    color: string;
    textColor: string;
    isVisible: boolean;
    isActive: boolean;
    isProgressVisible: boolean;
    show(): void;
    hide(): void;
    enable(): void;
    disable(): void;
    showProgress(leaveActive?: boolean): void;
    hideProgress(): void;
    onClick(callback: () => void): void;
    offClick(callback: () => void): void;
    setText(text: string): void;
    setParams(params: Record<string, unknown>): void;
  };
  BackButton: {
    isVisible: boolean;
    show(): void;
    hide(): void;
    onClick(callback: () => void): void;
    offClick(callback: () => void): void;
  };
  HapticFeedback: {
    impactOccurred(
      style: "light" | "medium" | "heavy" | "rigid" | "soft",
    ): void;
    notificationOccurred(type: "error" | "success" | "warning"): void;
    selectionChanged(): void;
  };
}

export function getTelegramWebApp(): TelegramWebApp | null {
  return window.Telegram?.WebApp ?? null;
}

export function getTelegramUser() {
  const webapp = getTelegramWebApp();
  return webapp?.initDataUnsafe?.user ?? null;
}

export function initTelegramApp() {
  const webapp = getTelegramWebApp();
  if (!webapp) return;

  webapp.ready();
  webapp.expand();
  webapp.setHeaderColor("#050608");
  webapp.setBackgroundColor("#050608");
  webapp.enableClosingConfirmation();
}

export function haptic(
  type: "impact" | "notification" | "selection",
  style?: string,
) {
  const webapp = getTelegramWebApp();
  if (!webapp) return;

  switch (type) {
    case "impact":
      webapp.HapticFeedback.impactOccurred(
        (style as "light" | "medium" | "heavy") || "medium",
      );
      break;
    case "notification":
      webapp.HapticFeedback.notificationOccurred(
        (style as "error" | "success" | "warning") || "success",
      );
      break;
    case "selection":
      webapp.HapticFeedback.selectionChanged();
      break;
  }
}
