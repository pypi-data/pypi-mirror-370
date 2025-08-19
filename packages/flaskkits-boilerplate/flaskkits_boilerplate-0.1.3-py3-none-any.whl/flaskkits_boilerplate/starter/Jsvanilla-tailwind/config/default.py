class DefaultConfig:
    DEBUG = True
    SECRET_KEY = 'supersecretkey'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:password@localhost/dbname'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
