from os import environ


class Config:
    DEBUG = True
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = environ.get('JWT_SECRET_KEY')

class Production(Config):
    SECRET_KEY = environ.get('SECRET_KEY_PROD')
    SQLALCHEMY_DATABASE_URI = environ.get('DB_URI_PROD')

class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = environ.get('SECRET_KEY_TEST')
    SQLALCHEMY_DATABASE_URI = environ.get('DB_URI_TEST')
    
    

configuration = {'production':Production, 'testing':TestingConfig}