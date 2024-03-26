
from datetime import datetime
from flask_login import login_required
import sqlalchemy
from app.cashflow.routes import insert_to_cashflow
from app.models.supplier import Supplier
from app.product import bp
from flask import flash, render_template, request, redirect, url_for
from app.models.product import Product,Inventory
from app import db


from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, IntegerField, DateField, DecimalField
from wtforms.validators import InputRequired, NumberRange, DataRequired
from flask_principal import Permission,RoleNeed
admin_permission = Permission(RoleNeed('admin'))
class InventoryForm(FlaskForm):
    product_id = IntegerField('Product ID', validators=[InputRequired()])
    supplier = SelectField('Supplier', choices=[],validators=[DataRequired()])
    stock_in_date = DateField('Stock In Date', validators=[InputRequired()])
    expiry_date = DateField('Expiry Date', validators=[InputRequired()])
    init_qty = IntegerField('Initial Quantity', validators=[InputRequired(),NumberRange(min=0)])
    cost_per_item = DecimalField('Cost Per Item', validators=[InputRequired(), NumberRange(min=0)])
    retail_price = DecimalField('Retail Price', validators=[InputRequired(), NumberRange(min=0)])

@bp.route('/inventory/', methods=['GET'])
def inventory_detail():
    id = request.args.get('inventory',None,int)
    inventory = Inventory.query.filter(Inventory.id == id).first()
    suppliers = Supplier.query.all()
    return render_template('/product/inventory_detail.html',inventory = inventory,suppliers=suppliers)

@bp.route('/<barcode>/inventory/create', methods=['POST'])
@login_required
@admin_permission.require(http_exception=401)
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
            insert_to_cashflow(
                particular=f'Stock in - <{product.Name}>',
                debit=0.00,
                credit=float(form.init_qty.data * form.cost_per_item.data)
            )
        except Exception as e:
            db.session.rollback()
            return f"error: {str(e)}",500
        
    return redirect(url_for("product.get_product",barcode=barcode))
