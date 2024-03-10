from datetime import date, datetime, timedelta
from statistics import mean
from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import extract

from config import Config
from app.extensions import db

from app.models.supplier import Supplier
from app.models.category import Category
from app.models.staff import Staff
from app.models.product import Product,Inventory
from app.models.supplier import Supplier

# from app.models.dailysalesreport import DailySalesReport,Sale
from app.models.sale import Sale,Sale_Item

import plotly.graph_objs as go
from plotly.subplots import make_subplots
from app.plotly_graphs import *

def check_inventory():
    products_below_safety = Product.query.filter(Product.Safety_quantity > Product.Inventories.any(Inventory.Available_QTY)).all()
    print(products_below_safety)
    return products_below_safety

# Define an event listener to update product status when inventory quantity changes
# @db.event.listens_for(db.Session, 'before_flush')
# def update_product_status(session, flush_context, instances):
#     for instance in session.dirty:
#         if isinstance(instance, Inventory):
#             # Check if the total quantity summed across all inventories becomes 0
#             total_quantity = sum(inv.Available_QTY for inv in instance.product.Inventories)
#             if total_quantity == 0:
#                 instance.product.Status = 'OutOfStock'
#         elif isinstance(instance, Product):
#             # If the user manually sets the product status to 'InStock', automatically change it to 'OutOfStock'
#             if instance.Status == 'InStock':
#                 instance.Status = 'OutOfStock'

def create_app(config_class = Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config['SECRET_KEY'] = 'your_secret_key_here'
    # app.config['SECRET_KEY'] = 'smart_key_fyp_project'
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
        # inventories = Inventory.query.all()
        # categories = Category.query.all()
        # products = Product.query.all()
        # Monthly Profit
        

        product_proportion = show_product_proportion_pie()
        sales_graph = show_sales_graph()
        turnover_bar = show_inventory_turnover_graph()
        vertical_product_bar = show_prodcut_vertical_bar()
        lost_cost_bar = show_product_lost_cost_bar()

        print(check_inventory())
        # Convert the pie chart to JSON format
        product_proportion_pie = product_proportion.to_json()
        sales_graph = sales_graph.to_json()
        turnover_bar = turnover_bar.to_json()
        vertical_product_bar = vertical_product_bar.to_json()

        lost_cost_bar =lost_cost_bar.to_json()
        product_count,sale_count,total_supplier,total_staff = all_Model_value_total()
        # total_suppkier = Supplier.query(db.func.sum())
        return render_template('index.html', sales_graph = sales_graph,
                               product_proportion_pie= product_proportion_pie,
                               turnover_bar = turnover_bar,
                               vertical_product_bar=vertical_product_bar,
                               lost_cost_bar = lost_cost_bar,
                               inventory_warning = check_inventory(),
                               product_count = product_count,sale_count = sale_count,total_supplier = total_supplier,total_staff = total_staff
        )
    

    


    @app.route('/init_data')
    def initdata():
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
            inventory1 = Inventory(product = product1,Supplier_id = supplier.id,StockInDate = datetime.strptime("2024-2-2", '%Y-%m-%d'),ExpiryDate = datetime.strptime("2025-4-30", '%Y-%m-%d'),Init_QTY=100,Available_QTY=100,Locked_QTY= 0,Lost_QTY=0,Sold_QTY=0,CostPerItem=2.50,RetailPrice=3.10)
            cat1 = Category(Name="Drink")
            cat2 = Category(Name="Snack")
            cat3 = Category(Name="Chocolate")
            cat4 = Category(Name="Milk")
            cat5 = Category(Name="Discount Packages")
            product1.Categories.append(cat2)
            product1.Categories.append(cat3)
            product1.Categories.append(cat5)

            db.session.add_all([product1])
            db.session.add_all([inventory1])
            db.session.add_all([cat1,cat2,cat3,cat4,cat5])
            db.session.commit()

        return redirect(url_for('/'))
    
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

def all_Model_value_total():
    total_supplier = Supplier.query.count()
    total_staff = Staff.query.count()
    total_products = Product.query.count()
    total_inventories = Inventory.query.count()
    total_categories = Category.query.count()
    out_of_stock_products = Product.query.filter_by(Status='OutOfStock').count()
    not_available_products = Product.query.filter_by(Status='NotAvailable').count()
    in_stock_products = Product.query.filter_by(Status='InStock').count()
    total_sold = db.session.query(db.func.sum(Inventory.Sold_QTY)).scalar()
    total_inventory_cost = db.session.query(db.func.sum(Inventory.CostPerItem * Inventory.Init_QTY)).scalar()
    below_safety_level_products = Product.query.filter(Product.Safety_quantity!=-1,Product.Safety_quantity > Product.Inventories.any(Inventory.Available_QTY)).count()
    expired_products = Inventory.query.filter(Inventory.ExpiryDate < date.today()).count()
    inventory_lost = db.session.query(db.func.sum(Inventory.Lost_QTY)).scalar()
    lost_cost = db.session.query(db.func.sum(Inventory.CostPerItem * Inventory.Lost_QTY)).scalar()


    # Sales Count
    total_sales = Sale.query.count()
    # Calculate total monthly profit
    current_month = datetime.now().month
    current_year = datetime.now().year
    total_monthly_profit = db.session.query(db.func.sum(Sale.Total - (Sale_Item.Quantity * Inventory.CostPerItem))) \
        .join(Sale_Item).join(Inventory).filter(db.func.extract('year', Sale.Date) == current_year, db.func.extract('month', Sale.Date) == current_month).scalar()
    # Calculate daily sales and daily profit
    today = date.today()
    total_daily_sales = Sale.query.filter_by(Date=today).count()
    total_daily_profit = db.session.query(db.func.sum(Sale.Total - (Sale_Item.Quantity * Inventory.CostPerItem))) \
        .join(Sale_Item).join(Inventory).filter(Sale.Date == today).scalar()
    
    

    # Create plotly visualization for products by status
    product_count = {'total':total_products,
                     'categories':total_categories,
                     'OutOfStock': out_of_stock_products, 
                     'NotAvailable': not_available_products,
                     'total_inventories':total_inventories,
                     'total_sold':total_sold,
                     'in_stock_products':in_stock_products,
                     'total_inventory_cost': total_inventory_cost,
                     'below_safety_level_products':below_safety_level_products,
                     'expired':expired_products,
                     'inventory_lost':inventory_lost,
                     'lost_cost':lost_cost
                     }
    
    sale_count = {'total_sales':total_sales,
                  'total_monthly_profit': "%.2f" % total_monthly_profit if total_monthly_profit else 0,
                  'total_daily_sales':total_daily_sales,
                  'total_daily_profit':  "%.2f" % total_daily_profit if total_daily_profit else 0
                  }
    return product_count,sale_count,total_supplier,total_staff

if __name__ == "__main__":
    app = create_app()

    app.run(debug=True)