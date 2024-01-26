from app.extensions import db

#class DB
class Category(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    category_name = db.Column(db.String, nullable=False)
    
    def __init__(self,category_name):
        self.category_name = category_name

    def _repr_(self):
        return f'<Category "{self.category_name}">'