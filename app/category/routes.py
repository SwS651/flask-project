from datetime import datetime
from app.category import bp
from app.models.category import Category
from flask import render_template, request, redirect, url_for
from app import db
from app.models.product import Inventory, Product
# from app.models.dailysalesreport import DailySalesReport, Sale

@bp.route('/', methods=['GET'])
def index():
    # categories = Category.query.all()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    categories = Category.query.order_by(Category.Name).paginate(page=page, per_page=per_page)
    print(categories.items)
    return render_template('product/categories.html', categories = categories)

# Search operation
@bp.route('/search', methods=['GET'])
def search_category():
    query = request.args.get('query',None)
    if not query or query.isspace():
        return redirect(url_for('category.index'))
    
    categories = Category.query.order_by(Category.Name).filter(Category.Name.ilike(f'%{query}%')).all()
    return render_template("product/categories.html",categories = categories)

# Read operation
@bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    # category = Category.query.get(category_id)
    category = Category.query.filter(Category.id == category_id)
    print(category)
    return render_template("product/categories.html",categories = category)

@bp.route('/create', methods=['GET','POST'])
def create_category():
    if request.method == 'POST':
        category = request.form['category_name']
        
        new_Category = Category(Name = category)

        db.session.add(new_Category)
        db.session.commit()

    return redirect(url_for('category.index'))

    

@bp.route('/<category_name>/edit', methods=['POST'])
def edit_category(category_name):
    category = db.one_or_404(db.select(Category).filter(Category.Name == category_name))
    print(category)
    if request.method == 'POST':
        # Update data from the form
        category.Name = request.form['category_name']

        
        # Commit changes to the database
        db.session.commit()

    return redirect(url_for('category.index'))

@bp.route('/<int:id>/delete', methods=['POST'])
def delete_category(id):
    category = Category.query.get_or_404(id)

    # Delete the inventory item from the database
    db.session.delete(category)
    db.session.commit()

    return redirect(url_for('category.index'))


@bp.route('/fggh', methods=['GET'])
def view_category():

    return "Here is Category"