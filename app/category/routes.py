from app.category import bp
from app.models.category import Category
from flask import render_template, request, redirect, url_for
from app import db

@bp.route('/')
def index():
    categories = Category.query.all()
    return render_template('admin/category_management.html', action="", categories = categories)


@bp.route('/create', methods=['GET','POST'])
def create_category():
    if request.method == 'POST':
        category = request.form['category_name']
        
        new_Category = Category(category_name = category)

        db.session.add(new_Category)
        db.session.commit()
        return redirect(url_for('category.index'))
     
    if request.method == 'GET':
        categories = Category.query.all()
        return render_template('admin/category_management.html',categories = categories,action = 'create_category',category = False)
    

@bp.route('/<category_name>/edit', methods=['POST'])
def edit_category(category_name):
    category = db.one_or_404(db.select(Category).filter_by(category_name=category_name))

    if request.method == 'POST':
        # Update data from the form
        category.category_name = request.form['category_name']

        
        # Commit changes to the database
        db.session.commit()

    return redirect(url_for('category.index'))

@bp.route('/<int:category_id>/delete', methods=['POST'])
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)

    # Delete the inventory item from the database
    db.session.delete(category)
    db.session.commit()

    return redirect(url_for('category.index'))


# @bp.route('/<int:category_id>', methods=['GET'])
# def view_category(category_id):
#     category = Category.query.get_or_404(category_id)
#     return render_template('category.html', categories=category) 
