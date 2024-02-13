from datetime import datetime,date, timedelta

from app.models.product import Product,Inventory
from app.models.staff import Staff
from app.sale import bp
from app.models.sale import Sale, Sale_Item
from flask import render_template, request, redirect, url_for
from app import db
@bp.route('/', methods=['GET','POST'])
def sales_index():
    sales, product_totals,staff_totals = get_Info()
    return render_template('sales/index.html',sales = sales,products = product_totals,staff_totals = staff_totals,date = date)


def get_Info():
    sales = Sale.query.order_by(Sale.Status).all()
    product_query_totals = db.session.query(Product.Name,db.func.sum(Sale_Item.Quantity).label("Quantity")).filter(Sale.Date == date.today(),Sale.id == Sale_Item.Report_id,Sale.Status == "paid",Inventory.Product_id == Product.id,Inventory.id == Sale_Item.Inventory_id).group_by(Product.Name).all()
    # today_records = Sale.query.filter(Sale.Date == date.today()).all()
    staff_query_totals = db.session.query(Sale.Staff_id,Staff.Name,db.func.sum(Sale.Total).label("Total_Amount"))\
                            .filter(Sale.Date == date.today(),Staff.id == Sale.Staff_id)\
                            .group_by(Sale.Staff_id)\
                            .all()

    return sales, product_query_totals, staff_query_totals

@bp.route('/search')
def search_sales():
    print("yess")
    sales, product_totals,staff_totals = get_Info()

    start_date = request.args.get('start_date')
    end_date =request.args.get('end_date')

    print(f"start date: {start_date}, enddate: {end_date}")
    # Convert string inputs to datetime objects
    start_date = datetime.strptime(start_date, '%Y-%m-%d') - timedelta(days=1)
    end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
    # Query database for records within the specified date range
    sales = Sale.query.filter(Sale.Date>=start_date,Sale.Date<=end_date).all()
        
    print(sales)
    return render_template('sales/index.html',sales = sales,products = product_totals,staff_totals = staff_totals,date = date)




def create_sale():
    sale = Sale(
        Staff_id=204542, 
        Date = datetime.today(), 
        Tax = 0,
        Discount = 0, 
        Type_Payment = "", 
        No_Refer = "", 
        Total = 0, 
        Status ="draft"
        )
    try:
        db.session.add(sale)
        db.session.commit()
        return sale
    except Exception as e:
        db.session.rollback()
        return None

def get_draft_sale():
    return Sale.query.filter(Sale.Status == "draft").first()

@bp.route('/checkout/', methods=['GET','POST'])
def show_checkout_page():
    products = Product.query.filter(Product.Status == "InStock").all()
    sale = get_draft_sale()
    if sale:
        sale.Staff_id = 204542
        sale.Date = datetime.today()
        update_sale_Total(sale.id)
        db.session.commit()

        total_inventory = [sum(inventory.Available_QTY for inventory in product.Inventories) for product in products]
    else:
        sale = create_sale()
    return render_template('sales/checkout.html',products=products,sale = sale)

@bp.route('/add',methods=["GET"])
def add_sale_item():
    item_id = request.args.get("item",None)
    if item_id:

        # query = db.session.query(Inventory)\
        #              .join(Product)\
        #              .filter(Inventory.Product_id == item_id, Inventory.Available_QTY > 0)\
        #              .order_by(Inventory.StockInDate)\
        #              .first()
        
        # if not query:
        #     print("No inventory found for the given product ID.")
        #     pass
        
        inventory = Inventory.query.filter(Inventory.Product_id == item_id, Inventory.Available_QTY > 0)\
                                   .order_by(Inventory.StockInDate).first()
        if inventory:

            sale = get_draft_sale()
            sale_item = Sale_Item.query.filter(Sale_Item.Inventory_id == inventory.id,Sale_Item.Report_id==sale.id).first()

            if sale_item:
                sale_item.Quantity += 1
            else:
                sale_item = Sale_Item(
                    sale = sale,
                    Inventory_id = inventory.id,
                    Quantity = 1,
                    SalePrice = inventory.RetailPrice
                )
                db.session.add(sale_item)
            inventory.Available_QTY -= 1
            inventory.Locked_QTY +=1
            db.session.commit()

    return redirect(url_for('sale.show_checkout_page'))


@bp.route('/<int:item>/delete',methods=["GET","POST"])
def remove_sale_item_from_checkout(item):
    sale_item = Sale_Item.query.get_or_404(item)
    if sale_item.Quantity > 1:
        sale_item.Quantity -= 1
    else:
        db.session.delete(sale_item)
    inventory = Inventory.query.get_or_404(sale_item.Inventory_id)
    inventory.Available_QTY += 1
    inventory.Locked_QTY -= 1
    db.session.commit()

    update_sale_Total(sale_item.Report_id)
    return redirect(url_for('sale.show_checkout_page')) 

@bp.route('/sale/<int:item>/delete',methods=["GET","POST"])
def remove_sale_items(item):
    sale_item = Sale_Item.query.get_or_404(item)
    sale = Sale.query.get_or_404(sale_item.Report_id)
    inventory = Inventory.query.filter(Inventory.id == sale_item.Inventory_id).first()
    count_sale_items = Sale_Item.query.filter(Sale_Item.Report_id == sale.id).count()
    if inventory:
        inventory.Available_QTY += sale_item.Quantity
        inventory.Sold_QTY = 0

    db.session.delete(sale_item)
    db.session.commit()
    print("count: ",count_sale_items)
    if count_sale_items <= 1:
        db.session.delete(sale)
        db.session.commit()

    return render_template('sales/saledetail.html',sale=sale)
    

@bp.route('/<int:id>/checkout',methods=["GET","POST"])
def finalize_checkout(id):
    sale =  Sale.query.get_or_404(id)
    update_sale_Total(sale.id)
    if request.method == "POST":
        tax = float(request.form["tax"])
        discount = float(request.form["discount"])
        no_refer = request.form["no_refer"]
        type_payment = request.form["type_payment"]
        if "custom_price" in request.form and request.form["custom_price"] == "True":
            total = float(request.form["total"])
        else:  
            total = (sale.Total + (sale.Total*(tax/100))) - (sale.Total * (discount/100))

        sale.Date = datetime.today()
        sale.Tax = tax
        sale.Discount = discount
        sale.No_Refer = no_refer
        sale.Type_Payment = type_payment
        sale.Total = "%.2f" % total
        sale.Status = "paid"
        db.session.commit()
    sale_item = Sale_Item.query.filter(Sale_Item.Report_id == sale.id).first()
    
    inventory = Inventory.query.filter(Inventory.id == sale_item.Inventory_id).first()
    inventory.Sold_QTY = sale_item.Quantity
    inventory.Locked_QTY = 0
    db.session.commit()
    print(inventory)

    return redirect(url_for("sale.sales_index"))

# def update_inventory
def update_sale_Total(id):
    sale = Sale.query.get_or_404(id)
    subtotal = sum(item.Quantity * item.SalePrice for item in sale.Sale_items)
    # for item in sale.Sale_items:
    #     print(item.Quantity * item.SalePrice)
    #     subtotal += (item.Quantity * item.SalePrice)
    sale.Total = subtotal
    db.session.commit()



@bp.route('/detail',methods=['GET'])
def get_sale_detail():
    id = request.args.get('id')
    sale = Sale.query.get_or_404(id)
    products = Product.query.all()
    
    # print(product)
    return render_template('sales/saledetail.html',sale = sale,products=products)

