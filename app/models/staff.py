from app.extensions import db
#User table DB
class Staff(db.Model):
    __tablename__ = "staff"
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String, unique=True, nullable=False)
    Email = db.Column(db.String, nullable=False)
    Password = db.Column(db.String, nullable=False)
    Role = db.Column(db.String, nullable=False)

    
    
    def __rer__(self):
        return f'<User {self.StaffName!r}'
    