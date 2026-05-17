"""
scraper.py — Récupère le prix m² Grande Rue, Le Plessis-Robinson
sur MeilleursAgents et l'ajoute au fichier data/prices.csv
"""

import csv
import os
import re
from datetime import date

import requests
from bs4 import BeautifulSoup

# ── Configuration ─────────────────────────────────────────────────────────────
URL = "https://www.meilleursagents.com/prix-immobilier/le-plessis-robinson-92350/grande-rue-2004252/"
CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "prices.csv")
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9",
}
# ──────────────────────────────────────────────────────────────────────────────


def fetch_price() -> dict | None:
    """Scrape la page et retourne un dict avec date + prix appart + prix maison."""
    try:
        resp = requests.get(URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERREUR] Impossible de joindre MeilleursAgents : {e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    # MeilleursAgents affiche les prix dans du texte du style "5 359 €"
    # On cherche les deux premières occurrences de prix m²
    prices_found = []
    for tag in soup.find_all(string=re.compile(r"\d[\s\u202f]\d{3}\s*€")):
        nums = re.findall(r"(\d[\s\u202f]\d{3})", tag)
        for n in nums:
            val = int(n.replace("\u202f", "").replace(" ", ""))
            if 1000 < val < 20000:   # filtre anti-faux-positifs
                prices_found.append(val)

    if not prices_found:
        print("[ERREUR] Aucun prix trouvé — la structure de la page a peut-être changé.")
        return None

    # Convention : premier prix = appartements, second = maisons (si dispo)
    prix_appart = prices_found[0] if len(prices_found) >= 1 else None
    prix_maison = prices_found[1] if len(prices_found) >= 2 else None

    return {
        "date": date.today().isoformat(),
        "prix_appart": prix_appart,
        "prix_maison": prix_maison,
    }


def save_to_csv(row: dict) -> None:
    """Ajoute une ligne au CSV (crée le fichier + header si nécessaire)."""
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    file_exists = os.path.isfile(CSV_PATH)

    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "prix_appart", "prix_maison"])
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

    print(f"[OK] Enregistré : {row}")


def main():
    print(f"[INFO] Collecte du prix m² — {date.today()}")
    row = fetch_price()
    if row:
        save_to_csv(row)
    else:
        print("[INFO] Aucune donnée enregistrée.")


if __name__ == "__main__":
    main()
