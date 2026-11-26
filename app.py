import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

from dotenv import load_dotenv
from flask import Flask, render_template

load_dotenv(Path(__file__).with_name(".env"))

app = Flask(__name__)

N8N_ARTICLES_URL = os.environ.get(
    "N8N_ARTICLES_URL",
    "http://127.0.0.1:5678/webhook/portfolio-articles"
)

CF_ACCESS_CLIENT_ID = os.environ.get("CF_ACCESS_CLIENT_ID")
CF_ACCESS_CLIENT_SECRET = os.environ.get("CF_ACCESS_CLIENT_SECRET")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/actualites-ia")
def ai_news():
    articles = []
    api_error = False

    try:
        headers = {
            "Accept": "application/json"
        }

        # Cloudflare Access authentication
        if N8N_ARTICLES_URL.startswith(
            "https://n8n.valerianbarreau.com/"
        ):
            if not CF_ACCESS_CLIENT_ID or not CF_ACCESS_CLIENT_SECRET:
                raise ValueError("Missing Cloudflare credentials")

            headers["CF-Access-Client-Id"] = CF_ACCESS_CLIENT_ID
            headers["CF-Access-Client-Secret"] = CF_ACCESS_CLIENT_SECRET

        request = Request(
            N8N_ARTICLES_URL,
            headers=headers,
            method="GET"
        )

        with urlopen(request, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))

        if isinstance(payload, dict):
            payload = payload.get("data", payload.get("articles", []))

        if not isinstance(payload, list):
            raise ValueError("n8n API response must be a JSON array")

        articles = [
            article for article in payload
            if isinstance(article, dict)
        ]

    except (OSError, ValueError):
        app.logger.exception("Could not load AI news from n8n")
        api_error = True

    return render_template(
        "actualites.html",
        articles=articles,
        api_error=api_error
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
