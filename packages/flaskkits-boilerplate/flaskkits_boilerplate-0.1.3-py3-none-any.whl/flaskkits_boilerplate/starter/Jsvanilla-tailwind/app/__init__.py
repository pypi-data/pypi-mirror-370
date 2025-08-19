from flask import Flask
from .extensions import db
from .blueprints import main

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object("config.default.DefaultConfig")
    db.init_app(app)

    from .routes.counter_routes import main
    app.register_blueprint(main, url_prefix='/')
    return app
