import express from "express";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();

const host = process.env.REMOTE_HUB_HOST || "0.0.0.0";
const port = Number(process.env.REMOTE_HUB_PORT || 3000);

// Minimal: serve the existing HTML UI
app.get(["/", "/mobile"], (_req, res) => {
  res.sendFile(path.join(__dirname, "mobile_dashboard.html"));
});

// Health endpoint for scripts
app.get("/health", (_req, res) => {
  res.status(200).json({ ok: true });
});

app.listen(port, host, () => {
  console.log(`[remote_hub] Node server listening on http://${host}:${port}`);
  console.log(`[remote_hub] Mobile UI: http://${host}:${port}/mobile`);
});
