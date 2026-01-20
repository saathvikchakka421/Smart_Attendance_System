import sqlite3
from werkzeug.security import generate_password_hash

DB = "attendance.db"

def connect():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin','faculty','student'))
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS courses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS enrollments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        UNIQUE(student_id, course_id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS attendance(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        class_date TEXT NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('Present','Absent')),
        marked_by INTEGER NOT NULL,
        UNIQUE(student_id, course_id, class_date)
    )
    """)

    conn.commit()

    # seed only if no users exist
    cur.execute("SELECT COUNT(*) AS c FROM users")
    if cur.fetchone()["c"] == 0:
        pwd = generate_password_hash("Password@123")
        cur.execute("INSERT INTO users(name,email,password_hash,role) VALUES (?,?,?,?)",
                    ("Admin", "admin@demo.com", pwd, "admin"))
        cur.execute("INSERT INTO users(name,email,password_hash,role) VALUES (?,?,?,?)",
                    ("Faculty", "faculty@demo.com", pwd, "faculty"))
        cur.execute("INSERT INTO users(name,email,password_hash,role) VALUES (?,?,?,?)",
                    ("Student One", "student1@demo.com", pwd, "student"))
        cur.execute("INSERT INTO users(name,email,password_hash,role) VALUES (?,?,?,?)",
                    ("Student Two", "student2@demo.com", pwd, "student"))

        cur.execute("INSERT INTO courses(code,title) VALUES (?,?)", ("CS101", "Programming Fundamentals"))

        # enroll students to CS101
        cur.execute("SELECT id FROM courses WHERE code='CS101'")
        course_id = cur.fetchone()["id"]
        cur.execute("SELECT id FROM users WHERE role='student'")
        student_ids = [r["id"] for r in cur.fetchall()]
        for sid in student_ids:
            cur.execute("INSERT OR IGNORE INTO enrollments(student_id, course_id) VALUES (?,?)", (sid, course_id))

        conn.commit()

    conn.close()
