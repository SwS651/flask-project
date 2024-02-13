
import pandas
import sqlalchemy
from app.models.category import Category
from app.models.supplier import Supplier
from app.product import bp
from flask import flash, render_template, request, redirect, url_for
from app.models.product import Product,product_category
from app import db

# from app.utils.import_.import_utils import *


@bp.route('/',methods=["GET"])
def index():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    query = request.args.get('query','')

    if query:
        products = Product.query.filter(
            db.or_(Product.BarCode.ilike(f'%{query}%'), Product.Name.ilike(f'%{query}%'))
        ).paginate(per_page=per_page, page=page, error_out=True)
    else:
        products = Product.query.paginate(per_page=per_page, page=page, error_out=True)

    categories = Category.query.all()
    
    return render_template('product/product.html', products=products,categories=categories)


@bp.route('/category/<category_name>')
def products_by_category(category_name):
    # Query the Category table to find the category with the given name
    category = Category.query.filter_by(Name=category_name).first()
    column_names = Product.metadata.tables['product'].columns.keys()
    categories = Category.query.all()
    if category:
        # If the category exists, retrieve all products associated with it
        products = category.products
        return render_template('product/product.html', products=products, column_names=column_names,categories=categories)
    else:
        # If the category does not exist, return an error message or handle it as you wish
        return "Category not found", 404


@bp.route('/<barcode>/', methods=['GET'])
def get_product(barcode):
    if barcode:
        product = db.one_or_404(db.select(Product).filter_by(BarCode=barcode))
        suppliers = Supplier.query.all()
        inventories = product.Inventories
        categories = Category.query.all()
        return render_template('product/detail.html', product=product,categories = categories,inventories = inventories,suppliers=suppliers)

    else:
        return redirect(url_for('product.index'))


@bp.route('/search/', methods=['GET'])
def search_product():

    query = request.args.get('query','')
    
    if not query:
        # Handle case when the query parameter is not provided
        return redirect(url_for('product.index'))
    
    products = Product.query.filter(
        db.or_(Product.BarCode.ilike(f'%{query}%'), Product.Name.ilike(f'%{query}%'))
    ).all()

    categories = Category.query.all()
    # Perform a search using an OR condition for barcode and product name
    # search_results = db.session.query(Product).filter(sqlalchemy.or_(str(Product.BarCode).upper() == query.upper(), (Product.Name).upper() == query.upper())).all()


    return render_template('product/product.html', products=products, categories=categories)




    
@bp.route('/create', methods=['GET', 'POST'])
def create_product():
    if request.method == 'POST':
        barcode = request.form['barcode']
        name = request.form['name']
        category_name = request.form['category']


        category = Category.query.filter(Category.Name == category_name).first()
        if not category:
            category = Category(Name=category_name)
            db.session.add(category)

        new_product = Product(
            BarCode=barcode,
            Name=name,
            Safety_quantity = -1,
            Status = "NotAvailable"
        )
        
        new_product.Categories.append(category)

        
        db.session.add(new_product)
        db.session.commit()

        return redirect(url_for('product.index'))
    categories = Category.query.all()
    return render_template('product/form.html',categories = categories)

    
@bp.route('/quick_edit/<barcode>', methods=['GET', 'POST'])
def quick_edit(barcode):
    product = db.one_or_404(db.select(Product).filter_by(BarCode=barcode))

    if request.method == 'POST':
        # Update data from the form
        product.BarCode = request.form['barcode'] if request.form['barcode'] else product.BarCode
        product.Name = request.form['name'] if request.form['barcode'] else product.Name
        product.Category = request.form['category'] if request.form['barcode'] else product.Category
        product.Quantity = request.form['quantity'] if request.form['barcode'] else product.Quantity
        product.RetailPrice = request.form['retail_price'] if request.form['barcode'] else product.RetailPrice

        try:
            # Commit changes to the database
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            
    return render_template(url_for('product.index'))


    # return render_template('product/detail.html', product=product,categories = categories,inventories = inventories)



@bp.route('/<barcode>/edit', methods=['GET', 'POST'])
def edit_product(barcode):
    product = Product.query.filter_by(BarCode=barcode).first_or_404()
    categories = Category.query.all()
    suppliers = Supplier.query.all()

    if request.method == 'POST':
        if "save_category" in request.form:
            product.Categories.clear()
            category_ids = request.form.getlist('category_ids')
            for cat in category_ids:
                product.Categories.append(Category.query.filter(Category.Name == cat).first())

        else:
            # Update data from the form
            # product.BarCode = request.form['barcode'] if request.form['barcode'] else product.BarCode
            # product.Name = request.form['name'] if request.form['barcode'] else product.Name
            # product.Safety_quantity = request.form['safety_quantity'] if request.form['barcode'] else product.Safety_quantity
            # product.Status = request.form['status'] if request.form['status'] else product.Status
            product.BarCode = request.form.get('barcode', product.BarCode)
            product.Name = request.form.get('name', product.Name)
            product.Safety_quantity = request.form.get('safety_quantity', product.Safety_quantity)
            product.Status = request.form.get('status', product.Status)
        try:
            db.session.commit()
            return redirect(url_for('product.edit_product',barcode=product.BarCode))
        except Exception as e:
            db.session.rollback()
            # return render_template('product/detail.html', product=product, error_message="Barcode already exists.")
            flash("Error occurred while updating the product.", "error")

    return render_template('product/detail.html', product=product,categories = categories, suppliers = suppliers )


@bp.route('/product/<int:id>/delete', methods=['POST'])
def delete_product(id):
    product = Product.query.get_or_404(id)

    product.delete()

    return redirect(url_for('product.index'))




