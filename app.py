import os, sqlite3, csv, io, json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "bet261.db")
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            league TEXT NOT NULL DEFAULT 'English League',
            round_name TEXT DEFAULT '',
            kickoff TEXT DEFAULT '',
            home TEXT NOT NULL,
            away TEXT NOT NULL,
            odd1 REAL,
            oddx REAL,
            odd2 REAL,
            home_goals INTEGER,
            away_goals INTEGER,
            status TEXT NOT NULL DEFAULT 'scheduled',
            source TEXT NOT NULL DEFAULT 'manual',
            created_at TEXT NOT NULL
        )
        """)
init_db()

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/api/status")
def status():
    # A real BET261 API connection must only be enabled with an official,
    # documented and authorized endpoint. No website login scraping here.
    configured = bool(os.getenv("BET261_API_BASE_URL") and os.getenv("BET261_API_TOKEN"))
    return jsonify({
        "app": "BET261 VIRTUAL AI PRO",
        "api_connector": "configured" if configured else "not_configured",
        "message": "Connecteur officiel non configuré. Utilisez l'import OCR ou la saisie contrôlée."
    })

@app.get("/api/matches")
def get_matches():
    with db() as conn:
        rows = conn.execute("SELECT * FROM matches ORDER BY id DESC LIMIT 500").fetchall()
    return jsonify([dict(r) for r in rows])

@app.post("/api/matches")
def add_match():
    data = request.get_json(force=True)
    home, away = (data.get("home") or "").strip(), (data.get("away") or "").strip()
    if not home or not away:
        return jsonify(error="Les deux équipes sont obligatoires."), 400
    def num(k):
        v = data.get(k)
        if v in (None, ""): return None
        try: return float(v)
        except (TypeError, ValueError): return None
    def goals(k):
        v = data.get(k)
        if v in (None, ""): return None
        try:
            n = int(v)
            return n if 0 <= n <= 30 else None
        except (TypeError, ValueError): return None
    hg, ag = goals("home_goals"), goals("away_goals")
    status_value = "finished" if hg is not None and ag is not None else "scheduled"
    with db() as conn:
        cur = conn.execute("""
          INSERT INTO matches
          (league,round_name,kickoff,home,away,odd1,oddx,odd2,home_goals,away_goals,status,source,created_at)
          VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
          (data.get("league") or "English League").strip(),
          (data.get("round_name") or "").strip(),
          (data.get("kickoff") or "").strip(),
          home, away, num("odd1"), num("oddx"), num("odd2"), hg, ag,
          status_value, (data.get("source") or "manual")[:30], datetime.utcnow().isoformat()
        ))
        new_id = cur.lastrowid
    return jsonify(ok=True, id=new_id)

@app.get("/api/stats")
def stats():
    with db() as conn:
        total = conn.execute("SELECT COUNT(*) n FROM matches").fetchone()["n"]
        finished = conn.execute("SELECT COUNT(*) n FROM matches WHERE status='finished'").fetchone()["n"]
        rows = conn.execute("""
          SELECT home_goals, away_goals, COUNT(*) n FROM matches
          WHERE status='finished' GROUP BY home_goals,away_goals
          ORDER BY n DESC, home_goals, away_goals LIMIT 10
        """).fetchall()
    return jsonify(total=total, finished=finished,
                   frequent_scores=[{"score": f"{r['home_goals']}-{r['away_goals']}", "count": r["n"]} for r in rows])

@app.get("/api/export.csv")
def export_csv():
    with db() as conn:
        rows = conn.execute("SELECT * FROM matches ORDER BY id").fetchall()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id","league","round","kickoff","home","away","odd1","oddx","odd2","home_goals","away_goals","status","source","created_at"])
    for r in rows:
        writer.writerow([r[k] for k in ["id","league","round_name","kickoff","home","away","odd1","oddx","odd2","home_goals","away_goals","status","source","created_at"]])
    mem = io.BytesIO(output.getvalue().encode("utf-8-sig"))
    mem.seek(0)
    return send_file(mem, mimetype="text/csv", as_attachment=True, download_name="bet261_historique.csv")

@app.post("/api/predict")
def predict():
    data = request.get_json(force=True)
    home, away = (data.get("home") or "").strip(), (data.get("away") or "").strip()
    if not home or not away:
        return jsonify(error="Saisissez les deux équipes."), 400
    with db() as conn:
        rows = conn.execute("""
          SELECT home_goals,away_goals FROM matches WHERE status='finished'
          ORDER BY id DESC LIMIT 300
        """).fetchall()
    if len(rows) < 10:
        return jsonify(available=False, message="Il faut au moins 10 résultats enregistrés pour afficher une analyse historique. Ce n'est pas une prédiction fiable.")
    from collections import Counter
    counts = Counter(f"{r['home_goals']}-{r['away_goals']}" for r in rows)
    top = [{"score": s, "count": n, "share_percent": round(n/len(rows)*100,1)} for s,n in counts.most_common(5)]
    return jsonify(available=True, sample_size=len(rows), historical_scores=top,
                   note="Fréquences historiques uniquement : elles ne garantissent pas le prochain résultat.")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
