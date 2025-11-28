from flask import Flask, render_template, request, redirect, session
import sqlite3, random, string

app = Flask(__name__)
app.secret_key = "becodosprimosmax"

# ---------- DATABASE ----------
def db():
    return sqlite3.connect("database.db")

with db() as con:
    con.execute("""
    CREATE TABLE IF NOT EXISTS keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT,
        usada INTEGER
    )
    """)

# ---------- UTIL ----------
def gerar_key():
    return "BDP-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=20))

# ---------- ROTAS ----------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if request.form["senha"] == "admin123":
            session["admin"] = True
            return redirect("/painel")
    return render_template("login.html")

@app.route("/painel")
def painel():
    if not session.get("admin"):
        return redirect("/login")

    con = db()
    keys = con.execute("SELECT * FROM keys").fetchall()
    return render_template("painel.html", keys=keys)

@app.route("/gerar")
def gerar():
    if not session.get("admin"):
        return redirect("/login")

    k = gerar_key()
    with db() as con:
        con.execute("INSERT INTO keys VALUES (NULL, ?, 0)", (k,))
    return redirect("/painel")

@app.route("/validar", methods=["POST"])
def validar():
    key = request.json["key"]
    con = db()
    res = con.execute(
        "SELECT * FROM keys WHERE key=? AND usada=0", (key,)
    ).fetchone()

    if res:
        con.execute("UPDATE keys SET usada=1 WHERE key=?", (key,))
        con.commit()
        return {"status":"ok"}
    return {"status":"invalid"}

app.run(host="0.0.0.0", port=10000)
