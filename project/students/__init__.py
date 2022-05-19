from flask import Blueprint

#special blueprint for the endpoints for the admin
student = Blueprint('student', __name__)

from . import student_routes