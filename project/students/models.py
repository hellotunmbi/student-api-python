from project import db, ma
from datetime import datetime, timedelta
from secrets import token_hex

# string used for the id for security reasons
id_number = token_hex(20)

# DB representation of the User table
# this table is for the Users that register students
class User(db.Model):
    __tablename__ = 'User'

    id = db.Column(db.String(100), primary_key=True, nullable=False, default=id_number)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(30), nullable=False, unique=True)
    gender = db.Column(db.String(10), default=None)
    password = db.Column(db.String(50), nullable=False, unique=True)
    date_joined = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

# DB representation of the student table
# this table is for the students being registered
class Student(db.Model):
    __tablename__ = 'Student'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), default=None)
    email = db.Column(db.String(30), unique=True, default=None)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    courses =  db.relationship('Course', cascade="all,delete", backref='student')

    def __repr__(self):
        return f'Student -- {self.first_name} {self.last_name}. age -- {self.age}'

class StudentSchema(ma.Schema):
    courses = ma.Nested("CourseSchema", many=True)  
    class Meta:
        fields = ("id", "first_name", "last_name", "email", "age", "gender", "date_added", "courses")


# DB representation of the course table
# relational table with students in the event that a student has more than one course
class Course(db.Model):
    __tablename__ = 'Course'

    id = db.Column(db.Integer, primary_key=True)
    course = db.Column(db.String(50), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('Student.id'), nullable=False)

class CourseSchema(ma.Schema):
    class Meta:
        fields = ("id", "course")

