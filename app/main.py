from io import BytesIO
from flask import Blueprint, render_template, request
from flask_login import login_required
import numpy as np
from app.cashflow.routes import get_month_value
from app.extensions import db

from datetime import date, datetime, timedelta
from app.models.cashflow import Cashflow
from app.models.supplier import Supplier
from app.models.category import Category
from app.models.user import User
from app.models.product import Product,Inventory
from app.models.supplier import Supplier
from app.models.sale import Sale,Sale_Item


from flask import send_file
from fpdf import FPDF
main = Blueprint('main', __name__)


@main.route('/imexport')
@login_required
def imexport_overview():
    
    return render_template('imexport_overview.html')


@main.route('/sales_report',methods=["GET"])
@login_required
def sales_report():
    return render_template('sales_report.html')

@main.route('/inventory_report',methods=["GET"])
@login_required
def inventory_report():
    products = Product.query.all()
    return render_template('inventory_report.html',products=products)

@main.route('/cashflow_report',methods=["GET"])
@login_required
def cashflow_report():
    
    return render_template('cashflow_report.html')

@main.route('/export_sales_report',methods=["GET"])
@login_required
def generate_sales_report():
    

    date = request.args.get("date")
    if not date:
        return render_template('sales_report.html')
    
    sales = Sale.query.filter_by(Date = date).all()
    total_amount = db.session.query(db.func.sum(Sale.Total)).filter_by(Date=date).scalar()
    total_qty =  db.session.query(db.func.sum(Sale_Item.Quantity)).filter(Sale.Date==date,Sale_Item.Report_id == Sale.id).scalar()
    product_query_totals = db.session.query(
                            Product.Name,Product.BarCode,db.func.sum(Sale_Item.Quantity).label("Quantity"),Sale.Type_Payment,Sale_Item.SalePrice,Sale.Discount).filter(Sale.Date == date,Sale.id == Sale_Item.Report_id,Sale.Status == "paid",Inventory.Product_id == Product.id,Inventory.id == Sale_Item.Inventory_id).group_by(Product.Name,Sale.Type_Payment,Sale.Discount).all()
    person =  db.session.query((User.Last_Name + ' ' + User.First_Name).label('Name'),User.StaffID).filter(Sale.Date == date, Sale.Staff_id == User.id).group_by((User.Last_Name + ' ' + User.First_Name).label('Name')).all()

    # Extract column names from the SQLAlchemy model
    # columns = [column.key for column in inspect(User).c]

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_font("helvetica", size=16,style="B")
    pdf.cell(40, 10, "SALES REPORT",align='CENTER', center=True)
    pdf.ln()
    pdf.set_y(25)
    pdf.set_font("helvetica", size=8,style='B')
    pdf.line(11, 31.5,34,31.5)
    pdf.cell(20, 10, "SALES PERSON: ")
    pdf.set_font(style='')
    pdf.set_x(40)

    for i ,p in enumerate(person):
        pdf.set_xy(35,25+(5 * i))
        pdf.cell(12, 10, f"{p.Name}")
        pdf.cell(20, 10, f"(ID: {p.StaffID})")
    pdf.set_xy(80,25)
    pdf.set_font(style='B')
    pdf.line(81, 31.5,89.5,31.5)
    pdf.cell(10, 10, "DATE: ")
    pdf.cell(40, 10, f"{date}")
    pdf.ln()


    pdf.set_font("helvetica", size=8)
    pdf.set_xy(150,25)
    pdf.cell(22, 10, "SALES QTY: ")
    pdf.cell(20, 10, f"{total_qty}")
    pdf.ln()
    pdf.set_xy(150,30)
    pdf.cell(22, 8, "SALES TOTAL: ")
    pdf.set_font("helvetica", size=8,style='B')
    pdf.cell(22, 8, f"{total_amount}")

    pdf.ln()
    pdf.ln()
    pdf.cell(40, 10, "ITEM DETAIL")
    pdf.ln()


    # Add table header
    pdf.set_fill_color(224, 235, 255)
    # Table Header
    pdf.cell(25, 7, 'BarCode', border=1, fill=True,align='CENTER')
    pdf.cell(40, 7, 'Name', border=1, fill=True,align='CENTER')
    pdf.cell(20, 7, 'Price', border=1, fill=True,align='CENTER')
    pdf.cell(13, 7, 'QTY', border=1, fill=True,align='CENTER')
    pdf.cell(25, 7, 'Payment', border=1, fill=True,align='CENTER')
    pdf.cell(20, 7, 'Amount', border=1, fill=True,align='CENTER')
    pdf.cell(20, 7, 'Discount', border=1, fill=True,align='CENTER')
    pdf.cell(23, 7, 'Total', border=1, fill=True,align='CENTER')
    pdf.ln()

    for product in product_query_totals:
        price_after_discount = np.round((product.SalePrice * product.Quantity)-((product.SalePrice * product.Quantity)*product.Discount/100),2)

        # Table data
        pdf.cell(25, 5, f"{product.BarCode}", border=1,align='CENTER')
        pdf.cell(40, 5, product.Name, border=1)
        pdf.cell(20, 5, f"{product.SalePrice}", border=1,align='CENTER')
        pdf.cell(13, 5, f"{product.Quantity}", border=1,align='CENTER')
        pdf.cell(25, 5, product.Type_Payment, border=1,align='CENTER')
        pdf.cell(20, 5, f"{product.SalePrice * product.Quantity}", border=1,align='CENTER')
        pdf.cell(20, 5, f"{np.round(((product.SalePrice * product.Quantity)*product.Discount/100),2)}", border=1,align='CENTER')
        pdf.cell(23, 5, f"{price_after_discount}", border=1,align='CENTER')

        pdf.ln()
    pdf.set_fill_color(200,200,200)
    pdf.cell(163.2, 5, "Total", border=1,align='CENTER',fill=True)
    pdf.cell(22.7, 5, f"{total_amount}", border=1,align='CENTER')
    pdf.ln()
    pdf.cell(80,10,'Note : This is an automatic generated document. No signature is required')
    pdf_bytes = BytesIO()
    pdf.output(pdf_bytes)
    pdf_bytes.seek(0)
    return send_file(pdf_bytes, as_attachment=False,download_name='sample1.pdf')


@main.route('/export_cashflow_report', methods=['GET'])
def generate_cashflow_report():

    
    date = datetime.strptime(request.args.get('date'),'%Y-%m')
    first_day_month, lastday_of_month, firstday_of_previous_month, lastday_of_previous_month = get_month_value(date.replace(day=1,hour=0,minute=0,second=0))
    cashflow = Cashflow.query.filter(Cashflow.date>=first_day_month,Cashflow.date<=lastday_of_month).order_by(Cashflow.date).all()

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_font("helvetica", size=16,style="B")
    pdf.cell(40, 10, "S-Mart Cash Flow REPORT",align='CENTER', center=True)
    pdf.ln()


    pdf.set_y(25)
    pdf.set_font("helvetica", size=8,style='B')
    pdf.line(11, 32,19.5,32)
    pdf.cell(20, 10, "DATE: ")
    pdf.set_font(style='')
    pdf.cell(40, 10, f"{first_day_month}   to   {lastday_of_month}")


    pdf.ln()
    pdf.ln()
    pdf.cell(40, 10, "DETAIL")
    pdf.ln()


    # Add table header
    pdf.set_fill_color(224, 235, 255)
    # for column_name in columns:
    #     pdf.cell(20, 10, column_name, border=1, fill=True)

    # Table Header
    pdf.cell(35, 7, 'Date', border=1, fill=True,align='CENTER')
    # pdf.cell(50, 7, 'StockI', border=1, fill=True,align='CENTER')
    pdf.cell(50, 7, 'Particulars', border=1, fill=True,align='CENTER')
    pdf.cell(20, 7, 'Debit', border=1, fill=True,align='CENTER')
    pdf.cell(20, 7, 'Credit', border=1, fill=True,align='CENTER')
    pdf.cell(20, 7, 'Balance', border=1, fill=True,align='CENTER')
    pdf.cell(40, 7, 'Remarks', border=1, fill=True,align='CENTER')

    pdf.ln()

    # Table data
    for c in cashflow:
        pdf.cell(35, 7, f'{c.date}', border=1,align='CENTER')
        pdf.cell(50, 7, f'{c.particulars}', border=1,align='CENTER')
        pdf.cell(20, 7, f'{c.debit}', border=1,align='CENTER')
        pdf.cell(20, 7, f'{c.credit}', border=1,align='CENTER')
        pdf.cell(20, 7, f'{c.balance}', border=1,align='CENTER')
        pdf.cell(40, 7,f'{c.remarks}', border=1)

        pdf.ln()

    pdf.ln()
    pdf.ln()
    pdf.cell(80,10,'Note : This is an automatic generated document. No signature is required')
    pdf_bytes = BytesIO()
    pdf.output(pdf_bytes)
    pdf_bytes.seek(0)
    return send_file(pdf_bytes, as_attachment=False,download_name='sample1.pdf')



@main.route('/export_inventory_report', methods=['GET'])
def generate_inventory_report():
    product_name = request.args.get('product')
    from_date = request.args.get('from_date')
    to_date =request.args.get('to_date')

    # Convert string inputs to datetime objects
    from_date = datetime.strptime(from_date, '%Y-%m-%d') - timedelta(days=1)
    to_date = datetime.strptime(to_date, '%Y-%m-%d') + timedelta(days=1)

    
    inventory = db.session.query(Product.BarCode,Inventory.Init_QTY,Supplier.Name.label("Supplier_Name"),Inventory.StockInDate,Inventory.ExpiryDate,Inventory.CostPerItem,Inventory.RetailPrice).filter(Product.Name == product_name,Supplier.id == Inventory.Supplier_id, Inventory.StockInDate>=from_date,Inventory.StockInDate<=to_date).group_by(Product.BarCode).all()
    total_amount = db.session.query(db.func.sum(Inventory.Init_QTY * Inventory.CostPerItem)).filter(Inventory.StockInDate>=from_date,to_date<= Inventory.StockInDate,Product.id == Inventory.Product_id).group_by({Product.Name}).all()
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_font("helvetica", size=16,style="B")
    pdf.cell(40, 10, "INVENTORY HISTORY REPORT",align='CENTER', center=True)
    pdf.ln()

    # Product
    pdf.set_y(25)
    pdf.set_font("helvetica", size=8,style='B')
    pdf.line(11, 31.5,22.5,31.5)
    pdf.cell(20, 10, "Product: ")
    pdf.cell(40, 10, f"{product_name}")
    pdf.set_font(style='')
    pdf.set_y(31)
    
    # Date
    pdf.set_font(style='B')
    pdf.line(11, 37.5,19.5,37.5)
    pdf.cell(20, 10, "DATE: ")
    pdf.set_font(style='')
    pdf.cell(40, 10, f"{from_date.date()} - {to_date.date()}")


    pdf.set_font("helvetica", size=8)
    pdf.set_xy(150,25)
    pdf.cell(22, 10, "COST AMOUNT: ")
    pdf.cell(20, 10, f"RM {total_amount}")
    pdf.ln()

    pdf.ln()
    pdf.cell(20, 10, "Supplier")
    pdf.cell(40, 10, "")
    pdf.set_y(46)
    pdf.cell(40, 10, "Categories")
    pdf.cell(40, 10, "")

    pdf.ln()
    pdf.cell(40, 10, "INVENTORY DETAIL")
    pdf.ln()


    # Add table header
    pdf.set_fill_color(224, 235, 255)
    # for column_name in columns:
    #     pdf.cell(20, 10, column_name, border=1, fill=True)

    # Table Header
    pdf.cell(20, 7, 'No', border=1, fill=True,align='CENTER')
    # pdf.cell(50, 7, 'StockI', border=1, fill=True,align='CENTER')
    pdf.cell(40, 7, 'StockInDate', border=1, fill=True,align='CENTER')
    pdf.cell(40, 7, 'ExpiryDate', border=1, fill=True,align='CENTER')
    pdf.cell(20, 7, 'Init_QTY', border=1, fill=True,align='CENTER')
    pdf.cell(20, 7, 'CostPerItem', border=1, fill=True,align='CENTER')
    pdf.cell(20, 7, 'Retail Price', border=1, fill=True,align='CENTER')
    pdf.cell(27, 7, 'Cost Total', border=1, fill=True,align='CENTER')
    pdf.ln()

    # Table data
    for i in range(1,60):
        pdf.cell(20, 7, '1', border=1,align='CENTER')
        pdf.cell(40, 7, '2/1/2024', border=1,align='CENTER')
        pdf.cell(40, 7, '1/7/2024', border=1,align='CENTER')
        pdf.cell(20, 7, '50', border=1,align='CENTER')
        pdf.cell(20, 7, '1.50', border=1,align='CENTER')
        pdf.cell(20, 7, '2.00', border=1,align='CENTER')
        pdf.cell(27, 7, '75.00', border=1,align='CENTER')
        pdf.ln()

    pdf.ln()
    pdf.ln()
    pdf.cell(80,10,'Note : This is an automatic generated document. No signature is required')
    pdf_bytes = BytesIO()
    pdf.output(pdf_bytes)
    pdf_bytes.seek(0)
    return send_file(pdf_bytes, as_attachment=False,download_name='sample1.pdf')
