from app.dailysalesreport import bp
from app.models.dailysalesreport import DailySalesReport
from flask import render_template, request, redirect, url_for
from app import db

@bp.route('/')
def index():
    reports = DailySalesReport.query.all()
    return render_template('report/index.html', action="", reports = reports)


@bp.route('/create', methods=['GET','POST'])
def create_dailysalesreport():
    if request.method == 'POST':
        
        return redirect(url_for('dailysalesreport.index'))
     
    if request.method == 'GET':
        reports = DailySalesReport.query.all()
        return render_template('dailysalesreport.html',reports = reports,action = 'create_dailysalesreport')
    

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_dailysalesreport(id):
    report = DailySalesReport.query.get_or_404(id)

    if request.method == 'POST':
        # Update data from the form
        

        
        # Commit changes to the database
        db.session.commit()

    reports = DailySalesReport.query.all()
    return render_template('report/index.html',action = 'edit_report',reports = reports)

@bp.route('/<int:id>/delete', methods=['POST'])
def delete_dailysalesreporty(id):
    report = DailySalesReport.query.get_or_404(id)

    # Delete the inventory item from the database
    db.session.delete(report)
    db.session.commit()

    return redirect(url_for('dailysalesreport.index'))

