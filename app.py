from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from datetime import date
from db import connect, init_db

app = Flask(__name__)
app.secret_key = "change-this-secret"

def current_user():
    return session.get("user")

def require_login():
    if not current_user():
        return redirect(url_for("login"))
    return None

@app.get("/")
def home():
    return redirect(url_for("dashboard") if current_user() else url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email=?", (email,))
        u = cur.fetchone()
        conn.close()

        if not u or not check_password_hash(u["password_hash"], password):
            flash("Invalid email or password", "danger")
            return render_template("login.html")

        session["user"] = {"id": u["id"], "name": u["name"], "role": u["role"], "email": u["email"]}
        return redirect(url_for("dashboard"))

    return render_template("login.html")

@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.get("/dashboard")
def dashboard():
    guard = require_login()
    if guard:
        return guard

    user = current_user()
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM courses ORDER BY code")
    courses = cur.fetchall()
    conn.close()
    return render_template("dashboard.html", user=user, courses=courses)

@app.route("/mark", methods=["GET", "POST"])
def mark():
    guard = require_login()
    if guard:
        return guard

    user = current_user()
    if user["role"] not in ("faculty", "admin"):
        flash("Only faculty/admin can mark attendance.", "warning")
        return redirect(url_for("dashboard"))

    course_id = request.args.get("course_id", "1")
    class_date = request.args.get("date", date.today().isoformat())

    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT * FROM courses WHERE id=?", (course_id,))
    course = cur.fetchone()

    cur.execute("""
        SELECT u.id, u.name
        FROM enrollments e
        JOIN users u ON u.id = e.student_id
        WHERE e.course_id = ?
        ORDER BY u.name
    """, (course_id,))
    students = cur.fetchall()

    if request.method == "POST":
        course_id = request.form["course_id"]
        class_date = request.form["class_date"]

        for s in students:
            status = request.form.get(f"status_{s['id']}", "Absent")
            cur.execute("""
                INSERT OR REPLACE INTO attendance(student_id, course_id, class_date, status, marked_by)
                VALUES (?,?,?,?,?)
            """, (s["id"], course_id, class_date, status, user["id"]))

        conn.commit()
        conn.close()
        flash("Attendance saved.", "success")
        return redirect(url_for("dashboard"))

    conn.close()
    return render_template("mark.html", user=user, course=course, students=students, class_date=class_date)

@app.get("/report")
def report():
    guard = require_login()
    if guard:
        return guard

    user = current_user()
    course_id = request.args.get("course_id", "1")

    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT * FROM courses WHERE id=?", (course_id,))
    course = cur.fetchone()

    if user["role"] == "student":
        cur.execute("""
            SELECT class_date, status
            FROM attendance
            WHERE student_id=? AND course_id=?
            ORDER BY class_date DESC
        """, (user["id"], course_id))
        rows = cur.fetchall()
        conn.close()
        return render_template("report.html", user=user, course=course, rows=rows, mode="student")

    cur.execute("""
        SELECT u.name,
               SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) AS present_count,
               COUNT(a.id) AS total_classes
        FROM enrollments e
        JOIN users u ON u.id = e.student_id
        LEFT JOIN attendance a
          ON a.student_id = u.id AND a.course_id = e.course_id
        WHERE e.course_id = ?
        GROUP BY u.id
        ORDER BY u.name
    """, (course_id,))
    rows = cur.fetchall()
    conn.close()
    return render_template("report.html", user=user, course=course, rows=rows, mode="faculty")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from datetime import date
from db import connect, init_db

app = Flask(__name__)
app.secret_key = "change-this-secret"

def current_user():
    return session.get("user")

def require_login():
    if not current_user():
        return redirect(url_for("login"))
    return None

@app.get("/")
def home():
    return redirect(url_for("dashboard") if current_user() else url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email=?", (email,))
        u = cur.fetchone()
        conn.close()

        if not u or not check_password_hash(u["password_hash"], password):
            flash("Invalid email or password", "danger")
            return render_template("login.html")

        session["user"] = {"id": u["id"], "name": u["name"], "role": u["role"], "email": u["email"]}
        return redirect(url_for("dashboard"))

    return render_template("login.html")

@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.get("/dashboard")
def dashboard():
    guard = require_login()
    if guard:
        return guard

    user = current_user()
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM courses ORDER BY code")
    courses = cur.fetchall()
    conn.close()
    return render_template("dashboard.html", user=user, courses=courses)

@app.route("/mark", methods=["GET", "POST"])
def mark():
    guard = require_login()
    if guard:
        return guard

    user = current_user()
    if user["role"] not in ("faculty", "admin"):
        flash("Only faculty/admin can mark attendance.", "warning")
        return redirect(url_for("dashboard"))

    course_id = request.args.get("course_id", "1")
    class_date = request.args.get("date", date.today().isoformat())

    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT * FROM courses WHERE id=?", (course_id,))
    course = cur.fetchone()

    cur.execute("""
        SELECT u.id, u.name
        FROM enrollments e
        JOIN users u ON u.id = e.student_id
        WHERE e.course_id = ?
        ORDER BY u.name
    """, (course_id,))
    students = cur.fetchall()

    if request.method == "POST":
        course_id = request.form["course_id"]
        class_date = request.form["class_date"]

        for s in students:
            status = request.form.get(f"status_{s['id']}", "Absent")
            cur.execute("""
                INSERT OR REPLACE INTO attendance(student_id, course_id, class_date, status, marked_by)
                VALUES (?,?,?,?,?)
            """, (s["id"], course_id, class_date, status, user["id"]))

        conn.commit()
        conn.close()
        flash("Attendance saved.", "success")
        return redirect(url_for("dashboard"))

    conn.close()
    return render_template("mark.html", user=user, course=course, students=students, class_date=class_date)

@app.get("/report")
def report():
    guard = require_login()
    if guard:
        return guard

    user = current_user()
    course_id = request.args.get("course_id", "1")

    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT * FROM courses WHERE id=?", (course_id,))
    course = cur.fetchone()

    if user["role"] == "student":
        cur.execute("""
            SELECT class_date, status
            FROM attendance
            WHERE student_id=? AND course_id=?
            ORDER BY class_date DESC
        """, (user["id"], course_id))
        rows = cur.fetchall()
        conn.close()
        return render_template("report.html", user=user, course=course, rows=rows, mode="student")

    cur.execute("""
        SELECT u.name,
               SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) AS present_count,
               COUNT(a.id) AS total_classes
        FROM enrollments e
        JOIN users u ON u.id = e.student_id
        LEFT JOIN attendance a
          ON a.student_id = u.id AND a.course_id = e.course_id
        WHERE e.course_id = ?
        GROUP BY u.id
        ORDER BY u.name
    """, (course_id,))
    rows = cur.fetchall()
    conn.close()
    return render_template("report.html", user=user, course=course, rows=rows, mode="faculty")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
