from app.extensions import db

#class DB
class DailySalesReport(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    Date = db.Column(db.Date, nullable=False)
    StockID = db.Column(db.String, nullable=False)
    SalesQuantity = db.Column(db.Integer, nullable=False)
    RetailPrice = db.Column(db.Double, nullable=False)
    Amount = db.Column(db.Double, nullable=False)
    
    def __init__(self,Date,StockID, SalesQuantity, RetailPrice, Amount):
        self.Date = Date
        self.StockID = StockID
        self.SalesQuantity = SalesQuantity
        self.RetailPrice = RetailPrice
        self.Amount = Amount

    def _repr_(self):
        return f'<SalesReport "{self.StockID}">'