from datetime import timedelta
import bcrypt
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, create_access_token, jwt_required, current_user, get_jwt
import re
import json

from project import db, jwt, flsk_bcrypt
from .models import User, Student, StudentSchema, Course, CourseSchema
from . import student

# this decorator and the one below are for assigning the current user from JWT
# to a user from the db when a user logs in
# I no sabi as e dey work but it sha works
@jwt.user_identity_loader
def user_identity_lookup(user):
    '''
    Automatically fetch authenticated
    user id from the database
    '''

    return user.id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_payload):
    '''
    Automatically load authenticated user object
    from database, making current_user available
    for route wrapped with the @jwt_required() decorator
    '''

    identity = jwt_payload["sub"]
    return User.query.filter_by(id=identity).one_or_none()


#this is an endpoint to register a user that wants to use the app to register students
@student.post('/register_user')
def register_user():
    try:
        data = request.get_json()

        # these are re patterns to make sure an inputed email is actually an email and an inputed password is strong
        email_regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        pass_reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,18}$"

        if not (re.search(email_regex, data["email"])):
            return jsonify({"error":"invalid email format"}), 400
        if not (re.search(pass_reg, data["password"])):
            return jsonify({"error":"invalid password format"}), 400

        # here, we are checking if a user exists in the database already
        user = User.query.filter_by(email=data["email"]).first()
        if user:
            return jsonify({"error":"user already exists"}), 400

        # in the case of a data breach the password has been encrypted by bcrypt
        # the encrypted passwords are stored in the database so only the setter of a password can access it
        crypt_pass = flsk_bcrypt.generate_password_hash(data["password"]).decode('utf-8')

        # storing names in lower case so that there can be consistency in the database
        stored_first_name = data["first_name"].lower()
        stored_last_name = data["last_name"].lower()

        # adding the user to the database
        new_user = User(
            first_name=stored_first_name,
            last_name=stored_last_name,
            email=data["email"],
            gender=data.get('gender', None),
            password=crypt_pass
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify ({"status":"reg successful"}), 200

    except Exception as e:
        db.session.rollback()
        print (e)
        return jsonify ({"error":"check input"}), 422

# this endpoint is for loging in users
@student.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()

        user = User.query.filter_by(email=data["email"]).first()

        # checking user existence and password
        if user:
            pass_check = flsk_bcrypt.check_password_hash(user.password, data["password"])
            if pass_check:
                # creating a jwt access token for authentication
                access_token = create_access_token(identity=user)
                return jsonify ({"status":"login success", 'access_token': access_token})
            else:
                return jsonify ({"status":"wrong password"})
            
        else:
            return jsonify ({"status":"email doesnt exist"})

    except Exception as e:
        print (e)
        return jsonify ({"error": "check inputs"}), 400

# endpoint for registering a student. Can only be accessed when a user logs in
@student.post('/register_student')
@jwt_required()
def register_student():
    try:
        data = request.get_json()

        email_regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'

        if not (re.search(email_regex, data["email"])):
            return jsonify({"error":"invalid email format"}), 400

        student = Student.query.filter_by(email=data["email"]).first()
        if student:
            return jsonify({"error":"student already exists"}), 400

        if isinstance(data['added_courses'], list) == False:
            return jsonify ({'status':'failed', 'msg':'please make sure courses are in a list'}), 400

        stored_first_name = data["first_name"].lower()
        stored_last_name = data["last_name"].lower()
    
        new_student = Student(
            first_name=stored_first_name,
            last_name=stored_last_name,
            age = int(data['age']),
            gender = data['gender'],
            email = data['email']
        )

        db.session.add(new_student)

        for course in data['courses']:
            added_course = Course(
                course = course.lower(),
                student = new_student
            )

            db.session.add(added_course)

        db.session.commit()

        return jsonify ({'status':'success', 'msg':f'Successfully added user {data["first_name"]} {data["last_name"]}'}), 200

    except Exception as e:
        db.session.rollback()
        print (e)
        return jsonify ({'status':'failed', 'msg':'something went wrong, please check inputs'}), 422

@student.put('/edit_student_info/<int:id>')
@jwt_required()
def edit_student_info(id):
    try:
        data = request.get_json()
        student = Student.query.get(id)

        if not student:
            return jsonify ({'status':'failed', 'msg':'User not found'}), 400

        if data.get('new_email'):
            check_student = Student.query.filter_by(email=data['new_email']).first()
            if check_student:
                return jsonify ({'status':'failed', 'msg':'email already in use'}), 400

        student.first_name = data['new_first_name'] if data.get('new_first_name') else student.first_name
        student.last_name = data['new_last_name'] if data.get('new_last_name') else student.last_name
        student.age = data['new_age'] if data.get('new_age') else student.age
        # this would be sooo weird XD XD XD
        student.gender = data['new_gender'] if data.get('new_gender') else student.gender
        student.email = data['new_email'] if data.get('new_email') else student.email

        db.session.commit()

        return jsonify ({'status':'success', 'msg':'details updated successfuly'}), 200

    except Exception as e:
        db.session.rollback()
        print (e)
        return jsonify ({'status':'failed', 'msg':'something went wrong, please check inputs'}), 422

@student.post('/add_student_courses/<int:id>')
@jwt_required()
def edit_student_courses(id):
    try:

        data = request.get_json()
        student = Student.query.get(id)

        courses = Course.query.filter_by(student_id=id).all()

        if not student:
            return jsonify ({'status':'failed', 'msg':'Student not found'}), 400

        # checking if a course is already listed with a user
        if (course.course for course in courses in data['added_courses']):
            return jsonify ({'status':'failed', 'msg':'please only add new courses'}), 400

        if isinstance(data['added_courses'], list) == False:
            return jsonify ({'status':'failed', 'msg':'please make sure courses are in a list'}), 400

        for course in data['added_courses']:
            new_courses = Course(
                course = course.lower(),
                user = student
            )

            db.session.add(new_courses)

        db.session.commit()

        return jsonify ({'status':'success', 'msg':'courses added successfuly'}), 200

    except Exception as e:
        db.session.rollback()
        print (e)
        return jsonify ({'status':'failed', 'msg':'something went wrong, please check inputs'}), 422

@student.delete('/delete_student_courses/<int:id>/<string:name>')
@jwt_required()
def delete_student_course(id, name):
    try:
        student = Student.query.get(id)

        if not student:
            return jsonify ({'status':'failed', 'msg':'Student not found'}), 400

        course = Course.query.filter_by(student_id=id, course=name.lower()).first()

        if course:
            db.session.delete(course)
            db.session.commit()
            return jsonify ({'status':'success', 'msg':'course deleted successfuly'}), 200

        else:
            return jsonify ({'status':'failed', 'msg':'course not found'}), 200

    except Exception as e:
        db.session.rollback()
        print (e)
        return jsonify ({'status':'failed', 'msg':'something went wrong, please check inputs'}), 422
        

@student.delete('/delete_student/<int:id>')
@jwt_required()
def delete_user(id):
    try:
        student = Student.query.get(id)

        if not student:
            return jsonify ({'status':'failed', 'msg':'Student not found'}), 400

        db.session.delete(student)
        db.session.commit()

        return jsonify ({'status':'success', 'msg':'student deleted successfuly'}), 200

    except Exception as e:
        db.session.rollback()
        print (e)
        return jsonify ({'status':'failed', 'msg':'something went wrong, please check inputs'}), 422

@student.get('/get_all_students')
@jwt_required()
def get_all_students():
    try:
        students = Student.query.all()

        if not students:
            return jsonify ({'status':'success', 'msg':'no students registered'}), 200

        serial_students = StudentSchema(many=True)

        return jsonify ({'status':'success', 'msg':'students retrieved successfully', 'data':serial_students.dump(students)}), 200

    except Exception as e:
        print (e)
        return jsonify ({'status':'failed', 'msg':'something went wrong'}), 422


@student.get('/get_student/<int:id>')
@jwt_required()
def get_student(id):
    try:
        student = Student.query.get(id)

        if not student:
            return jsonify ({'status':'failed', 'msg':'student not found'}), 200

        serial_student = StudentSchema()

        return jsonify ({'status':'success', 'msg':'student retrieved successfully', 'data':serial_student.dump(student)}), 200

    except Exception as e:
        print (e)
        return jsonify ({'status':'failed', 'msg':'something went wrong'}), 422



