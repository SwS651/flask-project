from app.staff import bp
from app.models.staff import Staff
from flask import render_template, request, redirect, url_for
from app import db

@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '')

    if search_query:
        staffs = Staff.query.filter(Staff.StaffName.ilike(f'%{search_query}%')).paginate(page, per_page=10)
    else:
        staffs = Staff.query.paginate(page = page, per_page=10)

    return render_template('admin/staff_management.html', staffs=staffs)
@bp.route('/create', methods=['GET','POST'])
def create_staff():
    if request.method == 'POST':
        new_staff = Staff(
            StaffID=request.form['staff_id'],
            StaffName=request.form['staff_name'],
            StaffEmail=request.form['staff_email'],
            Password=request.form['password'],
            Role=request.form['role']
        )
        db.session.add(new_staff)
        db.session.commit()
        return redirect(url_for('staff.index'))
    else:
        return render_template('admin/staff_form.html')

@bp.route('/<int:id>/edit', methods=['POST'])
def edit_staff(id):
    staff = Staff.query.get_or_404(id)


    staff.id = request.form['staff_id']
    staff.Name = request.form['staff_name']
    staff.Email = request.form['staff_email']
    staff.Role = request.form['role']
    db.session.commit()

    return redirect(url_for('staff.index'))

@bp.route('/<int:id>/delete', methods=['POST'])
def delete_staff(id):
    staff = Staff.query.get_or_404(id)
    db.session.delete(staff)
    db.session.commit()
    return redirect(url_for('staff.index'))

@bp.route('/<int:id>/', methods=['GET'])
def get_staff(id):
    staff = Staff.query.get_or_404(id)
    return render_template('admin/staff_form.html',staff = staff)