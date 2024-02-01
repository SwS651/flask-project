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



# import_method = ""
# temp_ExcelData = pd.DataFrame()
# proceed = False
# @bp.route('/import', methods=['GET','POST'])
# def import_stock():
#     global temp_ExcelData
#     global import_method
#     info_message = ""
    
#     if not temp_ExcelData.empty or not temp_ExcelData is None:
#         duplicate_rows, first_duplicate_rows, repeated_duplicate_rows = get_duplicate_rows_info(temp_ExcelData)
#         table = db.metadata.tables["stock"]
#         column_types = [str(col.type.python_type) for col in table.columns]
#         column_types.pop(0)
#     else:
#         return "Render failed"
    
#     return render_template('stock/import_wizard.html',column_names=temp_ExcelData.columns.values, 
#                                         first_duplicate_rows = first_duplicate_rows,
#                                         repeated_rows = repeated_duplicate_rows,
#                                         import_method = import_method,
#                                         column_types=column_types,
#                                         row_data=temp_ExcelData, zip=zip, info_message=info_message, pd=pd)


@bp.route('/file/upload', methods=['POST'])
def excel_upload():
    global temp_ExcelData
    global import_method


    if request.method == "POST":
        if import_method != "" or not import_method is None:
            import_method = ""
        try:
            excel_file = request.files['file']
            temp_ExcelData = pd.read_excel(excel_file)
            return redirect(url_for('stock.import_stock'))
        except Exception as e:
            print(f"Error reading Excel file: {e}")
            # return None
            return redirect(url_for('stock.import_stock'))
    

@bp.route('/file/validate', methods=['POST'])
def validate_exceldata():
    global temp_ExcelData
    global import_method
    if request.method == "POST":
        if import_method != "" or not import_method is None:
            import_method = ""
        temp_ExcelData = data_toDataFrame(request, 'column_names')
        temp_ExcelData = down_castDF(temp_ExcelData)
        print(temp_ExcelData.dtypes)
        check_duplicate_rows(temp_ExcelData)
            # info_message += "Data contains duplicate rows, are you sure you want to keep them in the record? "

        #  Step 2:Check for empty values
        check_empty_values(temp_ExcelData)
            # info_message += "Warning: There are NaN/Empty values in the DataFrame. Please review the data. (X) \n"
        print("before return: ",temp_ExcelData)
    
        return redirect(url_for('stock.import_stock'))

@bp.route('/file/final_validate', methods=['POST'])
def final_validate():
    global temp_ExcelData
    global import_method
    if request.method == "POST":
        custom_Table = db.metadata.tables["stock"]
        # temp_ExcelData = down_castDF(data)

        import_method = check_Import_condition(temp_ExcelData,custom_Table)
        check_writability_and_print(temp_ExcelData)
        temp_ExcelData = temp_ExcelData
        return redirect(url_for('stock.import_stock'))



def check_Import_condition(df_data,db_data,custom_model=False):
    global import_method
    # there is 3 return conditions: Smart import/ Custom-Advance Import and Import Failure
    df_columns = df_data.columns
    db_columns = [ column for column in db_data.columns.keys() if column not in "id"]
    db_types = [col.type.python_type for col in db_data.columns]
    db_types.pop(0)
    
    #convert DF data types to DB datatype first
    converted_dftypes = converto_dbtypes(df_data)

    # Condition Checking
    if len(df_columns) == len(db_columns) and list(set(db_types)) == list(set(converted_dftypes)):
        if (list(df_columns) == list(db_columns)):
            #"Perfect match (Smart Import)"
            import_method = "smart"
        else:
            #"Advance import (Custom/Advance Import) 1: all ok but column names not same; just change name to DB_column names"
            import_method = "smart"

    elif len(df_columns) == len(db_columns) and list(set(converted_dftypes)) >= list(set(db_types)):
        # "Advance import (Custom/Advance Import) 2: length of columns same but df_types >= dbtypes "
        import_method = "advance"

    elif len(df_columns) >= len(db_columns) and list(set(converted_dftypes)) >= list(set(db_types)):
       # "Advance import (Custom/Advance Import) 3: df_columns >= dbcolumns, but list of dftype >= dbtype"
        import_method = "advance"

    elif all(element in converted_dftypes for element in db_types):
        # "Advance import (Custom/Advance Import) 4: last compare data type got in db"
        import_method = "advance"

    if len(list(set(db_types))) > len(list(set(converted_dftypes))):
        print("Import failed (Import Failure)")
        import_method = "failure"
    return import_method

@bp.route('/file/insert_values', methods=['POST'])
def insert_toDB():
    global temp_ExcelData
    global import_method
    print(import_method)
    table = db.metadata.tables["stock"]
    db_columns = [column for column in table.columns.keys() if column not in "id"]
            
    if request.method == "POST":
        if import_method == "smart":
            # Replace column name of temp_data
            temp_ExcelData.columns = db_columns
            print(temp_ExcelData)
            if check_writability_and_print(temp_ExcelData):
                db.session.execute(table.insert(),temp_ExcelData.to_dict(orient='records'))
                db.session.commit()
                return redirect(url_for('stock.index'))
        if import_method == "advance":
            selected_df_column = request.form.getlist("column_index")
            data = temp_ExcelData[selected_df_column]
            data.columns = db_columns
            print(data)
            if check_writability_and_print(data):
                db.session.execute(table.insert(),data.to_dict(orient='records'))
                db.session.commit()
                return redirect(url_for('stock.index'))
            return f""
        import_method = "failure"
    return redirect(url_for('stock.index'))

