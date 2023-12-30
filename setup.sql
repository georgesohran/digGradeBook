/*
CREATE TABLE teachers
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    subject_id INTEGER,
    FOREIGN KEY(subject_id) REFERENCES subjects(id)
);


CREATE TABLE students
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL
);

CREATE TABLE subjects
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE students_grades
(
    student_id INTEGER,
    subject_id INTEGER,
    time TEXT NOT NULL,
    grade INTEGER NOT NULL,
    FOREIGN KEY(subject_id) REFERENCES subjects(id),
    FOREIGN KEY(student_id) REFERENCES students(id)
);

INSERT INTO subjects(name) VALUES ('math'),('english'),('phisics'),('computer sceince'),('history');

CREATE TABLE schedule
(
    monday TEXT,
    tuesday TEXT,
    wednesday TEXT,
    thirsday TEXT,
    friday TEXT,
    saturday TEXT,
    sunday TEXT
);


INSERT INTO schedule(monday,tuesday,wednesday,thirsday,friday,saturday,sunday)
    VALUES ('-','computer sceince','english','math','history','phisycs','math');


INSERT INTO students_grades (student_id, subject_id, time, grade)
    VALUES (9,5,'12.07.2023  12:43',5),(9,3,'12.07.2023  12:20',4),(9,2,'12.11.2023  12:43',3);


INSERT INTO schedule(monday,tuesday,wednesday,thirsday,friday,saturday,sunday)
    VALUES ('math','-','english','computer sceince','-','phisycs','history');
*/
