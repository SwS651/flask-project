from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_extensions(app):
    db.init_app(app)
    with app.app_context():
        #Create database
        db.create_all()