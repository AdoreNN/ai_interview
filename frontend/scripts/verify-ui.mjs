import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const app = readFileSync(resolve(root, "src/App.tsx"), "utf8");
const api = readFileSync(resolve(root, "src/api.ts"), "utf8");
const styles = readFileSync(resolve(root, "src/styles.css"), "utf8");

const requiredApiPaths = [
  "/auth/sign-up",
  "/auth/sign-in",
  "/sessions",
  "/resume",
  "/interview/start",
  "/interview/answer",
];

for (const path of requiredApiPaths) {
  if (!api.includes(path)) throw new Error(`missing API integration: ${path}`);
}

const requiredUiMarkers = [
  "AuthScreen",
  "SetupView",
  "InterviewView",
  "FeedbackCard",
  "Посмотреть демо",
  "Новое интервью",
  "Добавить PDF-резюме",
];

for (const marker of requiredUiMarkers) {
  if (!app.includes(marker)) throw new Error(`missing UI state: ${marker}`);
}

if (!styles.includes("@media (max-width: 760px)")) throw new Error("missing mobile layout");
if (!styles.includes("prefers-reduced-motion")) throw new Error("missing reduced motion support");
if (!styles.includes("focus-visible")) throw new Error("missing keyboard focus treatment");

console.log("UI contract verified");
