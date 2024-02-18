
from datetime import datetime
import sqlalchemy
from app.models.supplier import Supplier
from app.product import bp
from flask import flash, render_template, request, redirect, url_for
from app.models.product import Product,Inventory
from app import db


from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, IntegerField, DateField, DecimalField
from wtforms.validators import InputRequired, NumberRange, DataRequired

class InventoryForm(FlaskForm):
    product_id = IntegerField('Product ID', validators=[InputRequired()])
    supplier = SelectField('Supplier', choices=[],validators=[DataRequired()])
    stock_in_date = DateField('Stock In Date', validators=[InputRequired()])
    expiry_date = DateField('Expiry Date', validators=[InputRequired()])
    init_qty = IntegerField('Initial Quantity', validators=[InputRequired(),NumberRange(min=0)])
    cost_per_item = DecimalField('Cost Per Item', validators=[InputRequired(), NumberRange(min=0)])
    retail_price = DecimalField('Retail Price', validators=[InputRequired(), NumberRange(min=0)])

    # def __init__(self, *args, **kwargs):
    #     super(InventoryForm, self).__init__(*args, **kwargs)
    #     self.supplier.choices = [(supplier.id, supplier.Name) for supplier in Supplier.query.all()]


# @bp.route('/',methods=["GET"])
# def inventory_index():
#     page = request.args.get('page', 1, type=int)
#     per_page = request.args.get('per_page', 10, type=int)
#     inventories = Inventory.query.paginate(per_page=per_page, page=page, error_out=True)
#     return render_template("product/inventory.html",inventories =inventories)

    
# @bp.route('/<barcode>/inventory/create', methods=['GET', 'POST'])
def create_inventory(barcode,form = None):


    if barcode and form.validate_on_submit():
        product = db.one_or_404(db.select(Product).filter_by(BarCode=barcode))
        # storein_date = datetime.strptime(request.form['storein_date'], '%Y-%m-%d')
        # expiry_date = datetime.strptime(request.form['expiry_date'], '%Y-%m-%d')
        # supplier = Supplier.query.filter(Supplier.Name == request.form['supplier']).first()
        # quantity =int(request.form['quantity'])
        # costprice = float(request.form['cost_per_item'])
        # retailprice =float( request.form['retail_price'])

        new_inventory =  Inventory(
            product = product,
            Supplier_id =   form.supplier.data,
            StockInDate =   form.stock_in_date.data,
            ExpiryDate  =   form.expiry_date.data,
            Init_QTY    =   form.init_qty.data,
            Available_QTY=  form.init_qty.data,
            Locked_QTY  =   0,
            Lost_QTY    =   0,
            Sold_QTY    =   0,
            CostPerItem =   form.cost_per_item.data,
            RetailPrice =   form.retail_price.data
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
        
# @bp.route('/create', methods=['GET', 'POST'])
# def new_inventory():
#     if request.method == "POST":
        
#         if create_inventory(request.form["barcode"]):
#             return redirect(url_for("product.inventory_index"))
#         else:
#              return redirect(url_for("product.inventory_index"))
        

@bp.route('/<barcode>/inventory/create', methods=['POST'])
def add_inventory(barcode):

    form = InventoryForm()
    print(form.product_id.data)
    print(form.validate())
    if request.method=="POST" and barcode:
        product = db.one_or_404(db.select(Product).filter_by(BarCode=barcode))
        # storein_date = datetime.strptime(request.form['storein_date'], '%Y-%m-%d')
        # expiry_date = datetime.strptime(request.form['expiry_date'], '%Y-%m-%d')
        # supplier = Supplier.query.filter(Supplier.Name == request.form['supplier']).first()
        # quantity =int(request.form['quantity'])
        # costprice = float(request.form['cost_per_item'])
        # retailprice =float( request.form['retail_price'])

        new_inventory =  Inventory(
            product = product,
            Supplier_id =   form.supplier.data,
            StockInDate =   form.stock_in_date.data,
            ExpiryDate  =   form.expiry_date.data,
            Init_QTY    =   form.init_qty.data,
            Available_QTY=  form.init_qty.data,
            Locked_QTY  =   0,
            Lost_QTY    =   0,
            Sold_QTY    =   0,
            CostPerItem =   form.cost_per_item.data,
            RetailPrice =   form.retail_price.data
        )

        try:
            db.session.add(new_inventory)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
        
        return redirect(url_for("product.get_product",barcode=barcode))
