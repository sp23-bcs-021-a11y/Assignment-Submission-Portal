
import sqlite3
from urllib.parse import urlparse

from flask import Flask, render_template, request, redirect, url_for, flash


def create_app(test_config=None):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-secret-key"
    app.config["DATABASE"] = "submissions.db"

    if test_config:
        app.config.update(test_config)

    def get_db():
        conn = sqlite3.connect(app.config["DATABASE"])
        conn.row_factory = sqlite3.Row
        return conn

    def init_db():
        with get_db() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS submissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_name TEXT NOT NULL,
                    registration_number TEXT NOT NULL,
                    assignment_title TEXT NOT NULL,
                    submission_url TEXT NOT NULL
                )
            """)

    init_db()

    def valid_url(value):
        try:
            parsed = urlparse(value)
            return (
                parsed.scheme in ("http",)
                and bool(parsed.netloc)
                and "." in parsed.netloc
            )
        except ValueError:
            return False

    @app.route("/", methods=["GET", "POST"])
    def index():
        if request.method == "POST":
            student_name = request.form.get("student_name", "").strip()
            registration_number = request.form.get(
                "registration_number", ""
            ).strip()
            assignment_title = request.form.get(
                "assignment_title", ""
            ).strip()
            submission_url = request.form.get(
                "submission_url", ""
            ).strip()

            if not all([
                student_name,
                registration_number,
                assignment_title,
                submission_url
            ]):
                flash("All fields are required.", "error")
                return redirect(url_for("index"))

            if not valid_url(submission_url):
                flash("Invalid submission URL. Enter a valid HTTP or HTTPS URL.", "error")
                return redirect(url_for("index"))

            with get_db() as conn:
                conn.execute("""
                    INSERT INTO submissions
                    (student_name, registration_number,
                     assignment_title, submission_url)
                    VALUES (?, ?, ?, ?)
                """, (
                    student_name,
                    registration_number,
                    assignment_title,
                    submission_url
                ))

            flash("Assignment submitted successfully!", "success")
            return redirect(url_for("index"))

        with get_db() as conn:
            submissions = conn.execute(
                "SELECT * FROM submissions ORDER BY id DESC"
            ).fetchall()

        return render_template(
            "index.html",
            submissions=submissions
        )

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
