from flask import redirect, request, url_for,render_template
from flask_login import login_required
from app.models.product import LostReport, Product,Inventory
from app import db
from app.product import bp
# @bp.route('/lost_report',methods=["GET"])
# @login_required
# def get_inventory_():
#     # inventory_id = request.args.get('id',None,int)
#     # if inventory_id:
#     #     inventory =Inventory.query.filter(Inventory.id == inventory_id).first()
#     #     reports = LostReport.query.filter(LostReport.inventory_id == inventory_id).all()
#     # else:
#     #     return redirect(url_for('product.index'))
    
#     return render_template('/product/report_lost.html')

@bp.route('/lost_report', methods=['POST'])
def create_lost_report():
    data = request.json
    barcode = data.get('barcode')
    inventory_id = data.get('inventory_id')
    quantity_lost = data.get('quantity_lost')
    remark = data.get('remark')

    # Update inventory quantity and create lost report entry
    inventory = Inventory.query.get(inventory_id)
    if inventory:
        if inventory.quantity_on_hand >= quantity_lost:
            inventory.quantity_on_hand -= quantity_lost
            db.session.add(LostReport(barcode=barcode, inventory_id=inventory_id,
                                      quantity_lost=quantity_lost, remark=remark))
            db.session.commit()
            return jsonify({'message': 'Lost report created successfully'}), 201
        else:
            return jsonify({'error': 'Insufficient quantity in inventory'}), 400
    else:
        return jsonify({'error': 'Inventory not found'}), 404