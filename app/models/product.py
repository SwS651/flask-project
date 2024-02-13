from app import db

# Product model
product_category = db.Table('product_category',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)

class Product(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    BarCode = db.Column(db.BigInteger,nullable=False)
    Name = db.Column(db.String, nullable=False)
    Safety_quantity = db.Column(db.Integer,nullable=False)
    Status = db.Column(db.String, nullable=False) # "NotAvailable","OutOfStock","InStock"
    Inventories = db.relationship('Inventory',backref='product',lazy=True)  # Improved loading
    Categories = db.relationship('Category',secondary=product_category, backref=db.backref('products', lazy=True), lazy='subquery')
    
    
    def _repr_(self):
        return f'<Product "{self.Name}">'
    
    def delete(self):
        # Delete associated inventory items
        for inventory in self.Inventories:
            inventory.delete()
        # Delete the product itself
        db.session.delete(self)
        db.session.commit()
    
class Inventory(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    Product_id = db.Column(db.Integer,db.ForeignKey('product.id'),nullable=False)
    Supplier_id = db.Column(db.Integer,db.ForeignKey('supplier.id'),nullable=False)
    StockInDate = db.Column(db.Date, nullable=False)
    ExpiryDate = db.Column(db.Date, nullable=False)
    Init_QTY = db.Column(db.Integer, nullable=True)
    Available_QTY = db.Column(db.Integer, nullable=False)
    Locked_QTY = db.Column(db.Integer, nullable=False)
    Lost_QTY = db.Column(db.Integer, nullable=False)
    Sold_QTY = db.Column(db.Integer, nullable=False)
    CostPerItem = db.Column(db.Double, nullable=False)
    RetailPrice = db.Column(db.Double,nullable=False)

    def delete(self):
        # Perform any additional cleanup actions if needed
        # Delete the inventory item
        db.session.delete(self)
        db.session.commit()


    def _repr_(self):
        return f'<Stock "{self.StockInDate}...">'