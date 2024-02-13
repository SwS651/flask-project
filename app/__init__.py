from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from config import Config
from app.extensions import db

from app.models.supplier import Supplier
from app.models.category import Category
from app.models.staff import Staff
from app.models.product import Product,Inventory
from app.models.supplier import Supplier

# from app.models.dailysalesreport import DailySalesReport,Sale
from app.models.sale import Sale

def create_app(config_class = Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    #Initialize Flask extensions here
    from app.extensions import init_extensions
    init_extensions(app)  
    # Register blueprints her

    # from app.supplier import bp as supplier_bp
    # app.register_blueprint(category_bp,url_prefix='/suppliers')

    from app.category import bp as category_bp
    app.register_blueprint(category_bp,url_prefix='/category')

    from app.product import bp as product_bp
    app.register_blueprint(product_bp, url_prefix='/products')

    from app.staff import bp as staff_bp
    app.register_blueprint(staff_bp, url_prefix='/staff')
    
    from app.utils import bp as utils_bp
    app.register_blueprint(utils_bp, url_prefix='/utils')

    # from app.dailySalesReport import bp as sales_bp
    # app.register_blueprint(sales_bp, url_prefix='/daily_reports')
    from app.sale import bp as sales_bp
    app.register_blueprint(sales_bp, url_prefix='/sales')
    from app.supplier import bp as supplier_bp
    app.register_blueprint(supplier_bp, url_prefix='/suppliers')

    
        
    @app.route('/')
    def dashboard():
        product_table = db.metadata.tables["product"]
        # query = db.session.execute(db.select(product_table).filter_by(BarCode=3927110))
        query = Product.query.filter(Product.BarCode == 3927110)
        # product =  db.one_or_404(db.select(product_table).filter_by(BarCode=3927110))
        product = query if query.first() else None
        print(product)
        with app.app_context():
            staff = Staff(Name="admin",Email="admin@mail.com",Password="su",Role="admin")
            supplier = Supplier(Name="K Company",Address="Unkown Address")
            db.session.add_all([staff])
            db.session.add_all([supplier])
            db.session.commit()
            
            product1 = Product( BarCode = 3927110,Name = "KitKat",Safety_quantity = -1,Status="NotAvailable")
            inventory1 = Inventory(product = product1,Supplier_id = supplier.id,StockInDate = datetime.strptime("2023-11-12", '%Y-%m-%d'),ExpiryDate = datetime.strptime("2024-6-18", '%Y-%m-%d'),Init_QTY=100,Available_QTY=0,Locked_QTY= 0,Lost_QTY=0,Sold_QTY=100,CostPerItem=2.50,RetailPrice=3.00)
            inventory2 = Inventory(product = product1,Supplier_id = supplier.id,StockInDate = datetime.strptime("2024-1-12", '%Y-%m-%d'),ExpiryDate = datetime.strptime("2025-4-30", '%Y-%m-%d'),Init_QTY=100,Available_QTY=10,Locked_QTY= 0,Lost_QTY=0,Sold_QTY=90,CostPerItem=2.50,RetailPrice=3.00)
            inventory3 = Inventory(product = product1,Supplier_id = supplier.id,StockInDate = datetime.strptime("2024-2-2", '%Y-%m-%d'),ExpiryDate = datetime.strptime("2025-4-30", '%Y-%m-%d'),Init_QTY=100,Available_QTY=100,Locked_QTY= 0,Lost_QTY=0,Sold_QTY=0,CostPerItem=2.70,RetailPrice=3.10)
            cat1 = Category(Name="Drink")
            cat2 = Category(Name="Snack")
            cat3 = Category(Name="Chocolate")
            cat4 = Category(Name="Milk")
            cat5 = Category(Name="Discount Packages")
            product1.Categories.append(cat2)
            product1.Categories.append(cat3)
            product1.Categories.append(cat5)

            db.session.add_all([product1])
            db.session.add_all([inventory1,inventory2,inventory3])
            db.session.add_all([cat1,cat2,cat3,cat4,cat5])
            db.session.commit()

            # dailyreport = DailySalesReport(Staff_id = staff.id,Date = datetime.today())
            # salesdetail = Sale(daily_sales_report = dailyreport,Quantity=4,SalePrice=3.00,Subtotal=12.00,Inventory_id = inventory1.id)
            
            # db.session.add_all([dailyreport])
            # db.session.add_all([salesdetail])
            # db.session.commit()
        return render_template('index.html')
    
    @app.route('/login',methods=['GET','POST'])
    def login():
        info_message = ""
            
        if request.method == "POST":
            # users = db.session.execute(db.select(User).order_by(User.StaffName)).scalars()
            user = db.session.execute(db.select(Staff).filter_by(StaffEmail=request.form["email"],Password=request.form["password"])).scalar()
            if not user:
                info_message = "Invalid Email or Password!"
            else:
                
                return redirect(url_for('dashboard'))
            
        return render_template("login/login.html", info_message = info_message)


    return app

if __name__ == "__main__":
    app = create_app()

    app.run(debug=True)