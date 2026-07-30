"""
report.py — Génère une courbe d'évolution du prix m² et envoie un email.
Appelé automatiquement tous les 3 mois par GitHub Actions.
"""

import csv
import os
import smtplib
import io
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

import matplotlib
matplotlib.use("Agg")   # pas d'affichage graphique sur le serveur
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# ── Configuration — à remplir dans les GitHub Secrets ────────────────────────
GMAIL_USER   = os.environ["GMAIL_USER"]       # ex: moncompte@gmail.com
GMAIL_PASS   = os.environ["GMAIL_APP_PASS"]   # mot de passe d'application Gmail
EMAIL_TO     = os.environ["EMAIL_TO"]         # adresse destinataire

CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "prices.csv")
ADRESSE  = "Mettre l'adresse ou la ville ciblée ici"  # ex: "Paris 15e"
# ──────────────────────────────────────────────────────────────────────────────


def load_data() -> tuple[list, list, list]:
    """Charge le CSV et retourne (dates, prix_appart, prix_maison)."""
    dates, apparts, maisons = [], [], []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            dates.append(datetime.fromisoformat(row["date"]))
            apparts.append(float(row["prix_appart"]) if row["prix_appart"] else None)
            maisons.append(float(row["prix_maison"]) if row["prix_maison"] else None)
    return dates, apparts, maisons


def make_chart(dates, apparts, maisons) -> bytes:
    """Génère la courbe et retourne les octets PNG."""
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor("#0f172a")
    ax.set_facecolor("#1e293b")

    # Courbes
    if any(v for v in apparts):
        ax.plot(dates, apparts, color="#38bdf8", linewidth=2.5,
                marker="o", markersize=5, label="Appartements")
    if any(v for v in maisons):
        ax.plot(dates, maisons, color="#fb923c", linewidth=2.5,
                marker="s", markersize=5, label="Maisons")

    # Style
    ax.set_title(f"Prix m² — {ADRESSE}", color="white", fontsize=14, pad=15)
    ax.set_xlabel("Date", color="#94a3b8")
    ax.set_ylabel("€ / m²", color="#94a3b8")
    ax.tick_params(colors="#94a3b8")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    plt.xticks(rotation=30, ha="right")
    for spine in ax.spines.values():
        spine.set_edgecolor("#334155")
    ax.grid(color="#334155", linestyle="--", linewidth=0.7, alpha=0.7)
    legend = ax.legend(facecolor="#1e293b", edgecolor="#334155", labelcolor="white")

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return buf.read()


def send_email(chart_bytes: bytes, apparts: list, maisons: list) -> None:
    """Envoie l'email avec la courbe en pièce jointe."""
    today = date.today().strftime("%d/%m/%Y")

    # Derniers prix connus
    last_appart = next((v for v in reversed(apparts) if v), "N/A")
    last_maison = next((v for v in reversed(maisons) if v), "N/A")

    subject = f"📈 Rapport immobilier trimestriel — {ADRESSE} ({today})"
    body_html = f"""
    <html><body style="font-family:sans-serif;background:#f1f5f9;padding:24px">
      <div style="max-width:600px;margin:auto;background:white;border-radius:12px;padding:32px">
        <h2 style="color:#0f172a">Rapport trimestriel — Prix m²</h2>
        <p style="color:#475569">{ADRESSE}</p>
        <hr style="border:none;border-top:1px solid #e2e8f0"/>
        <p><strong>Derniers prix relevés ({today}) :</strong></p>
        <ul>
          <li>🏢 Appartements : <strong>{last_appart} €/m²</strong></li>
          <li>🏡 Maisons : <strong>{last_maison} €/m²</strong></li>
        </ul>
        <p style="color:#64748b;font-size:13px">
          La courbe d'évolution complète est jointe à cet email.<br>
          Source : MeilleursAgents.com
        </p>
      </div>
    </body></html>
    """

    msg = MIMEMultipart("related")
    msg["Subject"] = subject
    msg["From"]    = GMAIL_USER
    msg["To"]      = EMAIL_TO
    msg.attach(MIMEText(body_html, "html"))

    img = MIMEImage(chart_bytes, name=f"prix_m2_{date.today()}.png")
    img.add_header("Content-Disposition", "attachment",
                   filename=f"prix_m2_{date.today()}.png")
    msg.attach(img)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_PASS)
        server.sendmail(GMAIL_USER, EMAIL_TO, msg.as_string())

    print(f"[OK] Email envoyé à {EMAIL_TO}")


def main():
    print(f"[INFO] Génération du rapport — {date.today()}")
    dates, apparts, maisons = load_data()
    if not dates:
        print("[ERREUR] Aucune donnée dans le CSV.")
        return
    chart = make_chart(dates, apparts, maisons)
    send_email(chart, apparts, maisons)


if __name__ == "__main__":
    main()
