from app.services import flag_validator
from flask import request,redirect,url_for,Blueprint,render_template,flash
from flask_login import login_required,current_user

reactor_bp = Blueprint('reactor',__name__)
@reactor_bp.route('/reactor',methods = ['GET','POST'])
@login_required
def room():
    if current_user.has_fixed_room('medbay'):
        flash('medbay is already fixed')
        return redirect(url_for('dahsboard.index'))
    if request.method == 'POST':
        submitted_flag = request.form.get('flag','')
        result = flag_validator.validate_flag(current_user,'medbay',submitted_flag)

        if result['success']:
            flash(result['message'],'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash(result['message','success'])
            return redirect(url_for('reactor.room'))
