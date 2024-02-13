
from datetime import datetime
import sqlalchemy
from app.models.supplier import Supplier
from app.product import bp
from flask import render_template, request, redirect, url_for
from app.models.product import Product,Inventory
from app import db

# from app.utils.import_.import_utils import *

@bp.route('/',methods=["GET"])
def inventory_index():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    inventories = Inventory.query.paginate(per_page=per_page, page=page, error_out=True)
    return render_template("product/inventory.html",inventories =inventories)

    
# @bp.route('/<barcode>/inventory/create', methods=['GET', 'POST'])
def create_inventory(barcode,request):


    if barcode:
        product = db.one_or_404(db.select(Product).filter_by(BarCode=barcode))
        storein_date = datetime.strptime(request.form['storein_date'], '%Y-%m-%d')
        expiry_date = datetime.strptime(request.form['expiry_date'], '%Y-%m-%d')
        supplier = Supplier.query.filter(Supplier.Name == request.form['supplier']).first()
        quantity =int(request.form['quantity'])
        costprice = float(request.form['cost_per_item'])
        retailprice =float( request.form['retail_price'])

        new_inventory =  Inventory(
            product = product,
            Supplier_id = supplier.id,
            StockInDate =storein_date,
            ExpiryDate = expiry_date,
            Init_QTY=quantity,
            Available_QTY = quantity,
            Locked_QTY = 0,
            Lost_QTY = 0,
            Sold_QTY = 0,
            CostPerItem=costprice,
            RetailPrice=retailprice
        )

        try:
            db.session.add(new_inventory)
            db.session.commit()

            return True
        except Exception as e:
            db.session.rollback()
            return False
    else:
        return False

    # if request.method == 'GET':
    #     table = db.metadata.tables["category"]
    #     categories = db.session.execute(db.select(table)).fetchall()
    #     return render_template('product/form.html', categories = [cat[1] for cat in categories])
        
@bp.route('/create', methods=['GET', 'POST'])
def new_inventory():
    if request.method == "POST":
        
        if create_inventory(request.form["barcode"],request):
            return redirect(url_for("product.inventory_index"))
        else:
             return redirect(url_for("product.inventory_index"))
        

@bp.route('/<barcode>/inventory/create', methods=['POST'])
def add_inventory(barcode):
    if request.method == "POST":
        
        if create_inventory(barcode,request):
            return redirect(url_for("product.inventory_index"))
        else:
             return redirect(url_for("product.inventory_index"))