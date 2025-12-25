import os
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

HOST = os.environ.get("REMOTE_HUB_HOST", "0.0.0.0")
PORT = int(os.environ.get("REMOTE_HUB_API_PORT", "8503"))

@app.get("/stats")
def stats():
    # Minimal placeholder payload; wire your real revenue/orders logic here.
    return jsonify({
        "status": "online",
        "revenue": "1.250,00",
        "orders": 24,
        "host": HOST,
        "port": PORT,
    })

@app.get("/health")
def health():
    return jsonify({"ok": True})

if __name__ == "__main__":
    print(f"[remote_hub] Python API listening on http://{HOST}:{PORT}")
    app.run(host=HOST, port=PORT)
