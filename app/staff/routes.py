from app.staff import bp
from app.models.staff import Staff
from flask import render_template, request, redirect, url_for
from app import db

@bp.route('/')
def index():
    staffs = Staff.query.all()
    column_names = Staff.metadata.tables['staff'].columns.keys()
    return render_template('admin/staff_management.html', action="", staffs = staffs,column_names =column_names)


@bp.route('/create', methods=['GET','POST'])
def create_staff():
    if request.method == 'POST':
        new_staff = Staff(
            StaffID = request.form['staff_id'],
            StaffName = request.form['staff_name'],
            StaffEmail = request.form['staff_email'],
            Password = request.form['password'],
            Role = request.form['role']
        )
        db.session.add(new_staff)
        db.session.commit()
        return redirect(url_for('staff.index'))
     
    if request.method == 'GET':
        staffs = Staff.query.all()
        return render_template('admin/staff_form.html')
    

@bp.route('/<id>/edit', methods=['GET', 'POST'])
def edit_staff(id):
    staff = db.one_or_404(db.select(Staff).filter_by(StaffID=id))

    if request.method == 'POST':
        # Update data from the form
        staff.StaffID = request.form['staff_id']
        staff.StaffName = request.form['staff_name']
        staff.StaffEmail = request.form['staff_email']
        staff.Role = request.form['role']
        

        
        # Commit changes to the database
        db.session.commit()

    
    return redirect(url_for('staff.index'))

@bp.route('/<string:id>/delete', methods=['POST'])
def delete_staff(id):
    staff = db.one_or_404(db.select(Staff).filter_by(StaffID=id))
    # staff = Staff.query.get_or_404(id)

    # Delete the inventory item from the database
    db.session.delete(staff)
    db.session.commit()

    return redirect(url_for('staff.index'))

