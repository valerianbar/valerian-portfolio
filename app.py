import json
import os
from pathlib import Path
from urllib.request import urlopen

from dotenv import load_dotenv
from flask import Flask, render_template

load_dotenv(Path(__file__).with_name(".env"))

app = Flask(__name__)
N8N_ARTICLES_URL = os.environ.get(
    "N8N_ARTICLES_URL", "http://127.0.0.1:5678/webhook/portfolio-articles"
)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/actualites-ia")
def ai_news():
    articles = []
    api_error = False
    try:
        with urlopen(N8N_ARTICLES_URL, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if isinstance(payload, dict):
            payload = payload.get("data", payload.get("articles", []))
        if not isinstance(payload, list):
            raise ValueError("n8n API response must be a JSON array")
        articles = [article for article in payload if isinstance(article, dict)]
    except (OSError, ValueError, json.JSONDecodeError):
        app.logger.exception("Could not load AI news from n8n at %s", N8N_ARTICLES_URL)
        api_error = True
    return render_template("actualites.html", articles=articles, api_error=api_error)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
