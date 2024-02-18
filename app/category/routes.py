
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired,DataRequired,Length

from app.category import bp
from app.models.category import Category
from flask import render_template, request, redirect, url_for
from app import db
# from app.models.dailysalesreport import DailySalesReport, Sale

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[InputRequired(),DataRequired()])




@bp.route('/', methods=['GET'])
def index():
    form = CategoryForm()
    # categories = Category.query.all()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    categories = Category.query.order_by(Category.Name).paginate(page=page, per_page=per_page)
    # print(categories.items)
    return render_template('product/categories.html', categories = categories, form = form)

# Search operation
@bp.route('/search', methods=['GET'])
def search_category():
    query = request.args.get('query',None)
    form = CategoryForm()
    if not query or query.isspace():
        return redirect(url_for('category.index'))
    
    categories = Category.query.order_by(Category.Name).filter(Category.Name.ilike(f'%{query}%')).all()
    return render_template("product/categories.html",categories = categories,form=form)

# Read operation
@bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    # category = Category.query.get(category_id)
    category = Category.query.filter(Category.id == category_id)
    form=CategoryForm()
    # print(category)
    return render_template("product/categories.html",categories = category,form=form)

@bp.route('/create', methods=['GET','POST'])
def create_category():
    form=CategoryForm()
    print(form.validate_on_submit())
    if form.validate_on_submit():
        category = form.name.data
        print("category",category)
        
        new_Category = Category(Name = category)

        db.session.add(new_Category)
        db.session.commit()
    categories = Category.query.all()

    # return redirect(url_for('category.index'))
    return render_template("product/categories.html",categories = categories,form=form)

    

@bp.route('/<category_name>/edit', methods=['POST'])
def edit_category(category_name):
    category = db.one_or_404(db.select(Category).filter(Category.Name == category_name))
    form = CategoryForm(obj=category)
    if form.validate():
        # Update data from the form
        category.Name = form.name.data

        
        # Commit changes to the database
        db.session.commit()
        return redirect(url_for('category.index'))
    else:
        return render_template("product/categories.html",categories = Category.query.all(),form=form)

@bp.route('/<int:id>/delete', methods=['GET'])
def delete_category(id):
    category = Category.query.get_or_404(id)

    # Delete the inventory item from the database
    db.session.delete(category)
    db.session.commit()

    return redirect(url_for('category.index'))

