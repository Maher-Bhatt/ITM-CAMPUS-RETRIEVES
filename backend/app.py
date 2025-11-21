from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "supersecret"

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ---------------- DATABASE ---------------- #
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# Create tables if not exist
with get_db() as db:
    db.execute("""CREATE TABLE IF NOT EXISTS lost (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
        location TEXT,
        description TEXT,
        email TEXT,
        image TEXT
    )""")

    db.execute("""CREATE TABLE IF NOT EXISTS found (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
        location TEXT,
        description TEXT,
        email TEXT,
        sq TEXT,
        image TEXT
    )""")


# ---------------- USER HOME ---------------- #
@app.route("/")
def home():
    return render_template("user.html")

# ---------------- LOST SUBMIT ---------------- #
@app.post("/submit_lost")
def submit_lost():
    file = request.files.get("image")
    filename = None

    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    with get_db() as db:
        db.execute("""
            INSERT INTO lost (name, category, location, description, email, image)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            request.form["name"],
            request.form["category"],
            request.form["location"],
            request.form["description"],
            request.form["email"],
            filename
        ))
        db.commit()

    return "<h1 style='color:green'>Lost Item Submitted Successfully!</h1>"

# ---------------- FOUND SUBMIT ---------------- #
@app.post("/submit_found")
def submit_found():
    file = request.files.get("image")
    filename = None

    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    with get_db() as db:
        db.execute("""
            INSERT INTO found (name, category, location, description, email, sq, image)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            request.form["name"],
            request.form["category"],
            request.form["location"],
            request.form["description"],
            request.form["email"],
            request.form["sq"],
            filename
        ))
        db.commit()

    return "<h1 style='color:green'>Found Item Submitted Successfully!</h1>"

# ---------------- ADMIN LOGIN ---------------- #
@app.route("/admin", methods=["GET", "POST"])
def adminlogin():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "itm":
            session["admin"] = True
            return redirect("/dashboard")
        return "Invalid login!"

    return render_template("adminlogin.html")

# ---------------- ADMIN DASHBOARD ---------------- #
@app.route("/dashboard")
def dashboard():
    if "admin" not in session:
        return redirect("/admin")

    db = get_db()
    lost_items = db.execute("SELECT * FROM lost").fetchall()
    found_items = db.execute("SELECT * FROM found").fetchall()

    return render_template("admindashboard.html", lost=lost_items, found=found_items)

# ---------------- LOGOUT ---------------- #
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/admin")

if __name__ == "__main__":
    app.run()

