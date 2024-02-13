import numpy as np
import pandas as pd
import sqlalchemy
from app.stock import bp
from flask import render_template, request, redirect, url_for
from app.models.stock import Stock
from app.models.staff import Staff
from app import db
from datetime import date, datetime
from pandas.api.types import is_datetime64_any_dtype as is_datetime

# from app.utils.import_.import_utils import *

@bp.route('/')
@bp.route('/<int:page_num>')
def index(page_num=1):
    stocks = Stock.query.paginate(per_page=10, page=page_num, error_out=True)
    column_names = Stock.metadata.tables['stock'].columns.keys()
    # column_names = [column for column in Stock.metadata.tables['Stock'].columns.keys()]
    return render_template('stock/index.html',stocks = stocks,column_names = column_names)

@bp.route('/stock/create', methods=['GET','POST'])
def create_stock():

    if request.method == 'POST':
        barcode = request.form['barcode']
        stock_name = request.form['stock_name']
        category = request.form['category']
        stock_in_date = datetime.strptime(request.form['stock_in_date'], '%Y-%m-%d')
        expiry_date =  datetime.strptime(request.form['expiry_date'], '%Y-%m-%d')
        quantity = request.form['quantity']
        cost_price_per_item = request.form['cost_price_per_item']
        retail_price = request.form['retail_price']

        new_stock = Stock(
            BarCode = barcode,
            StockName = stock_name, 
            Category = category,
            StockInDate = stock_in_date,
            ExpiryDate =  expiry_date,
            Quantity = quantity,
            CostPricePerItem = cost_price_per_item,
            RetailPrice = retail_price
        )


        db.session.add(new_stock)
        db.session.commit()
        return(url_for('stock.index'))
    if request.method == 'GET':
        return render_template('stock/form.html')

@bp.route('/stock/<barcode>/edit', methods=['GET', 'POST'])
def edit_stock(barcode):
    print('Type of barcode: ',type(barcode))
    #This code is using the keywords other than primary key to get record
    #Please check https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/queries/ to know more
    # stock = db.session.execute(db.select(Stock).filter_by(BarCode=barcode)).scalar_one()
    stock = db.one_or_404(db.select(Stock).filter_by(BarCode=barcode))
    print('stock:',stock)
    if request.method == 'POST':
        # Update data from the form
        stock.BarCode = request.form['barcode']
        stock.StockName = request.form['stock_name']
        stock.Category = request.form['category']
        stock.StockInDate = datetime.strptime(request.form['stock_in_date'], '%Y-%m-%d')
        stock.ExpiryDate =  datetime.strptime(request.form['expiry_date'], '%Y-%m-%d')
        stock.Quantity = request.form['quantity']
        stock.CostPricePerItem = request.form['cost_price_per_item']
        stock.RetailPrice = request.form['retail_price']

        # Commit changes to the database
        db.session.commit()
        return redirect(url_for('stock.index'))

    return render_template('stock/form.html', stock=stock)  

@bp.route('/stock/<int:stock_id>/delete', methods=['POST'])
def delete_stock(stock_id):
    stock = Stock.query.get_or_404(stock_id)

    # Delete the stock item from the database
    db.session.delete(stock)
    db.session.commit()

    return redirect(url_for('stock.index'))


@bp.route('/stock/<int:stock_id>', methods=['GET'])
def view_stock(stock_id):
    stock = Stock.query.get_or_404(stock_id)
    return render_template('stock/view.html', stock=stock) 



@bp.route('/<string:_name>/', methods=['GET'])
def viewImport(_name):
    request.form.get('_name')
    print(_name)
    return _name

