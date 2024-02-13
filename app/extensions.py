
from flask_sqlalchemy import SQLAlchemy

# from app.models.product import Product, Inventory
db = SQLAlchemy()

def init_extensions(app):
    db.init_app(app)
    with app.app_context():
        #Create database
        db.create_all()

