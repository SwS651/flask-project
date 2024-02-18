
from app.staff import bp
from app.models.staff import Staff
from flask import flash, render_template, request, redirect, url_for
from app import db

from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, PasswordField, RadioField, SelectField, StringField, ValidationError
from wtforms.validators import InputRequired,Email, Length, EqualTo,NumberRange,DataRequired

class CreateStaffForm(FlaskForm):
    id = IntegerField("Staff ID")
    name = StringField('Name', validators=[InputRequired(), Length(max=100)])
    email = StringField('Email', validators=[InputRequired(), Email(), Length(max=50)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password')])
    # role = StringField('Role', validators=[InputRequired(), Length(max=20)])
    role = SelectField('Role', choices=[('admin', 'Admin'), ('staff', 'Staff')], validators=[InputRequired()])
    auto_generate_id = BooleanField('Automatically generate ID',default=True)

    def validate_id(self, field):
        if not self.auto_generate_id.data:  # Check if auto_generate_id is unchecked
            # If auto_generate_id is unchecked, check if ID is provided
            if not field.data:
                raise ValidationError('ID is required if not automatically generated')
            # Check if the ID is already in use
            if Staff.query.filter_by(id=field.data).first():
                raise ValidationError('ID already exists')

    
    def validate_role(self, field):
        if field.data not in ['admin', 'staff']:
            raise ValidationError('Invalid role.')
        
    def validate_name(self, field):
        # Check if the name already exists in the database
        if Staff.query.filter_by(Name=field.data).first():
            raise ValidationError('Name already exists.')
    def validate_email(self, field):
        if Staff.query.filter(Staff.Email == field.data, Staff.id != field.data).first():
            raise ValidationError('Email is already in use')
    
    def validate_id(self, field):
        if not self.auto_generate_id.data:  # Check if auto_generate_id is unchecked
            # If auto_generate_id is unchecked, check if ID is provided
            if not field.data:
                raise ValidationError('ID is required if not automatically generated')
            # Check if the ID is already in use
            if Staff.query.filter_by(id=field.data).first():
                raise ValidationError('ID already exists')
        
class EditStaffForm(FlaskForm):
    id = IntegerField("Staff ID")
    name = StringField('Name', validators=[InputRequired(), Length(max=100)])
    email = StringField('Email', validators=[InputRequired(), Email(), Length(max=50)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password')])
    # role = StringField('Role', validators=[InputRequired(), Length(max=20)])
    role = SelectField('Role', choices=[('admin', 'Admin'), ('staff', 'Staff')], validators=[InputRequired()])
    
            

        


@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '')
    form = EditStaffForm()
    if search_query:
        staffs = Staff.query.filter(Staff.StaffName.ilike(f'%{search_query}%')).paginate(page, per_page=10)
    else:
        staffs = Staff.query.paginate(page = page, per_page=10)

    return render_template('admin/staff_management.html', staffs=staffs,form =form)
@bp.route('/add', methods=['GET','POST'])
def create_staff():
    form = CreateStaffForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        role = form.role.data
        
        if form.auto_generate_id.data:
            id = None  # Let the database handle ID generation
        else:
            id = form.id.data
        
        newStaff = Staff(Name=name, Email=email, Password=password, Role=role, id=id)

        db.session.add(newStaff)
        db.session.commit()
        return redirect(url_for('staff.index'))
    else: 
        return render_template('admin/staff_form.html',form = form,action="add")


@bp.route('/<int:id>/delete', methods=['POST'])
def delete_staff(id):
    staff = Staff.query.get_or_404(id)
    db.session.delete(staff)
    db.session.commit()
    return redirect(url_for('staff.index'))

@bp.route('/<int:id>/edit', methods=['GET','POST'])
def get_staff(id):
    staff = Staff.query.get_or_404(id)
    form = EditStaffForm(obj=staff)
    print(staff.Name)

    if form.validate_on_submit():
        staff.id = form.id.data
        staff.Name = form.name.data
        staff.Password = form.password.data
        staff.Email = form.email.data
        staff.Role = form.role.data
        # form.populate_obj(staff)
        db.session.commit()
        flash('Staff member updated successfully!', 'success')
        return redirect(url_for('staff.index'))
    else:
        return render_template('admin/staff_form.html',staff = staff,form =  form, id=id, action ="edit")
    

    

@bp.route('/<int:id>/quick_edit', methods=['GET','POST'])
def quick_edit(id):
    staff = Staff.query.get_or_404(id)
    form = EditStaffForm(obj=staff)
    if request.method =="POST":

        staff.id = form.id.data
        staff.Name = form.name.data
        staff.Email = form.email.data
        db.session.commit()
        flash('Staff member updated successfully!', 'success')
        return redirect(url_for('staff.index'))
    else:
        return render_template('admin/staff_management.html',staffs = Staff.query.all(), form =  form)
    
@bp.route('/search')
def search_staff():
    keyword = request.args.get('q','')
    staffs = Staff.query.filter(db.or_(Staff.id.ilike(f'%{keyword}%'), Staff.Name.ilike(f'%{keyword}%')))
    return render_template('admin/staff_management.html', staffs=staffs)
