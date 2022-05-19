from flask import Flask
from .config import configuration, TestingConfig
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
ma = Marshmallow()
jwt = JWTManager()
flsk_bcrypt = Bcrypt()

def create_app(config_type=configuration['testing']):
    app = Flask(__name__)
    CORS(app)
    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    flsk_bcrypt.init_app(app)
    app.config.from_object(config_type)

    from .students import student as student_details
    app.register_blueprint(student_details, url_prefix='/api/v1/investor')

    return app