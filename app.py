from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from functions import login_required

from werkzeug.security import check_password_hash, generate_password_hash

import datetime

import os.path
import sqlite3

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "database.db")


if __name__ == "__main__":
    app.run(debug=True)



@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



@app.route("/register", methods=["POST","GET"])
def register():
    session.clear()

    db = sqlite3.connect(db_path, check_same_thread=False)
    cur = db.cursor()
    if request.method == "POST":
        password = request.form.get("password")
        password2 = request.form.get("password2")
        name = request.form.get("name")
        type = request.form.get("type")
        if type == "teacher":
            subject = request.form.get("subject")
            if subject not in ["math", "history", "english","computer sceince"]:
                return render_template("register.html", messege="invalid subject")

        if not password or not password2 or not name or not type:
            return render_template("register.html", messege="missing password or name or type")
        if type not in ["teacher", "student"]:
            return render_template("register.html", messege="invalid type")
        if password != password2:
            return render_template("register.html", messege="invalid repeat password")


        if type == "teacher":
            subject_id = db.execute("SELECT id FROM subjects WHERE name == ?", (subject,)).fetchall()
            subject_id = subject_id[0]
            subject_id = [i for i in subject_id][0]

            if (subject,) not in db.execute("SELECT name FROM subjects").fetchall():
                return render_template("register.html",messege="invalid subject")

            cur.execute("INSERT INTO teachers (name,password_hash,subject_id) VALUES(?,?,?)",(name, generate_password_hash(password), subject_id))
            db.commit()

        elif type == "student":
            cur.execute("INSERT INTO students (name,password_hash) VALUES(?,?)", (name, generate_password_hash(password)))
            db.commit()

        session["user_id"] = cur.execute(f"SELECT id FROM {type}s WHERE name == ?", (name,)).fetchall()

        session["user_type"] = type

        db.close()

        return redirect("/")

    else:
        db.close()

        return render_template("register.html", messege="OK")

@app.route("/login", methods=["POST","GET"])
def login():
    session.clear()

    db = sqlite3.connect(db_path, check_same_thread=False)
    cur = db.cursor()
    if request.method == "POST":
        name = request.form.get("name")
        type = request.form.get("type")
        password = request.form.get("password")

        if not name or not type or not password:
            return render_template("login.html" ,messege="missing name, type or password")

        if type not in ["teacher", "student"]:
            return render_template("login.html", messege="invalid type")

        all_names = cur.execute(f"SELECT name FROM {type}s")
        all_names = [i[0] for i in all_names]

        if name not in all_names:
            return render_template("login.html", messege="the name is not registrated")

        act_password = cur.execute(f"SELECT password_hash FROM {type}s WHERE name == ?", (name,)).fetchall()[0]
        if check_password_hash(act_password[0], password):
            return render_template("login.html", messege="invalid password")


        session["user_id"] = cur.execute(f"SELECT id FROM {type}s WHERE name == ?", (name,)).fetchall()

        session["user_type"] = type

        db.close()

        return redirect("/")
    else:
        db.close()
        return render_template("login.html", messege="OK")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


#sheared functions for both student and teacher
@app.route("/")
@login_required
def main_page():
    db = sqlite3.connect(db_path, check_same_thread=False)
    if session["user_type"] == "teacher":
        schedule = db.execute("SELECT * FROM schedule").fetchall()

        students = db.execute("SELECT name FROM students").fetchall()

        subject = db.execute("SELECT subject_id FROM teachers WHERE id == ?", (session["user_id"][0][0],)).fetchall()

        grades = {}

        for student in students:
            grade = db.execute("SELECT AVG(grade) FROM students_grades WHERE student_id == (SELECT id FROM students WHERE name == ?) AND subject_id == ?", (student[0],subject[0][0])).fetchall()

            if not grade[0][0] :
                grades[student[0]] = 0
            else:
                grades[student[0]] = grade[0][0]

        subject = db.execute("SELECT name FROM subjects WHERE id == ?", subject[0]).fetchall()

        db.close()
        return render_template("teacher/index.html", students=students , schedule=schedule , grades = grades , subject=subject)

    elif session["user_type"] == "student":
        schedule = db.execute("SELECT * FROM schedule").fetchall()

        all_subject_ids = db.execute("SELECT subject_id FROM students_grades WHERE student_id == ?", (session["user_id"][0][0],)).fetchall()

        bad_subjects = []

        averege_grades = {}

        for sub in all_subject_ids:
            subject = db.execute("SELECT name FROM subjects WHERE id == ?", sub).fetchall()
            grade = db.execute("SELECT AVG(grade) FROM students_grades WHERE subject_id == ? AND student_id == ?", (sub[0], session["user_id"][0][0])).fetchall()
            if grade[0][0] < 4:
                sub_name = db.execute("SELECT name FROM subjects WHERE id == ?", sub).fetchall()
                bad_subjects.append(sub_name[0][0])

            if grade[0][0] == None:
                averege_grades[subject[0][0]] = 0
            else:
                averege_grades[subject[0][0]] = grade[0][0]

        db.close()
        return render_template("student/index.html", schedule=schedule, bad_subjects=bad_subjects, averege_grades=averege_grades)

    else:
        db.close()
        return render_template("layout.html")

@app.route("/schedule")
@login_required
def schedule():
    db = sqlite3.connect(db_path, check_same_thread=False)
    schedule = db.execute("SELECT * FROM schedule").fetchall()

    db.close()

    return render_template("schedule.html", schedule=schedule)


#some functions for the students
@app.route("/grades")
@login_required
def grades():
    db = sqlite3.connect(db_path, check_same_thread=False)

    grades = db.execute("SELECT students_grades.grade, students_grades.time, subjects.name FROM students_grades INNER JOIN subjects ON students_grades.subject_id = subjects.id WHERE student_id = ?", (session["user_id"][0][0],)).fetchall()

    subjects = db.execute("SELECT name FROM subjects").fetchall()

    averege_grades = {}

    for subject in subjects:
        averege = db.execute("SELECT AVG(grade) FROM students_grades WHERE student_id == ? AND subject_id == (SELECT id FROM subjects WHERE name == ?)",(session["user_id"][0][0], subject[0])).fetchall()
        if averege[0][0] == None:
            averege_grades[subject[0]] = 0
        else:
            averege_grades[subject[0]] = averege[0][0]

    db.close()
    return render_template("student/grades.html",grades=grades, subjects=subjects, averege=averege_grades)



#some functions for teacher
@app.route("/students", methods=["POST","GET"])
@login_required
def students():
    db = sqlite3.connect(db_path, check_same_thread=False)
    if request.method == "POST":
        students_names = db.execute("SELECT name FROM students").fetchall()
        students_ids = db.execute("SELECT id FROM students").fetchall()

        for student,id in zip(students_names,students_ids):
            if not request.form.get(student[0]):
                continue
            if not 0 < int(request.form.get(student[0])) <= 5:
                db.close()
                return render_template("students.html")

            db.execute("INSERT INTO students_grades (student_id, subject_id, time, grade) VALUES (?,(SELECT subject_id FROM teachers WHERE id == ?),?,?)", (id[0], session["user_id"][0][0],datetime.datetime.now(), request.form.get(student[0]))).fetchall()
            db.commit()

        db.close()
        return redirect("/")
    else:
        grades = db.execute("SELECT students_grades.grade, students.name FROM students_grades INNER JOIN students ON students_grades.student_id = students.id WHERE subject_id = (SELECT subject_id FROM teachers WHERE id == ?)", (session["user_id"][0][0],)).fetchall()

        students = db.execute("SELECT name FROM students").fetchall()

        averege_grades = {}

        for student in students:
            averege = db.execute("SELECT AVG(grade) FROM students_grades WHERE student_id == (SELECT id FROM students WHERE name == ?) AND subject_id == (SELECT subject_id FROM teachers WHERE id == ?)",(student[0] ,session["user_id"][0][0],)).fetchall()
            if averege[0][0] == None:
                averege_grades[student[0]] = 0
            else:
                averege_grades[student[0]] = averege[0][0]

        db.close()
        return render_template("teacher/students.html", grades=grades, students=students, averege=averege_grades)
