from app.extensions import db
#User table DB
class Staff(db.Model):
    __tablename__ = "staff"
    id = db.Column(db.Integer, primary_key=True)
    StaffID = db.Column(db.String,unique=True,nullable=False)
    StaffName = db.Column(db.String, unique=True, nullable=False)
    StaffEmail = db.Column(db.String, nullable=False)
    Password = db.Column(db.String, nullable=False)
    Role = db.Column(db.String, nullable=False)

    def __init__(self,StaffID,StaffName, StaffEmail, Password,Role):
        self.StaffID = StaffID
        self.StaffName = StaffName
        self.StaffEmail = StaffEmail
        self.Password = Password
        self.Role = Role
    
    def __rer__(self):
        return f'<User {self.StaffName!r}'
    