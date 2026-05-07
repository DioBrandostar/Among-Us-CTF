from app.services import flag_validator
from flask import request,redirect,render_template,url_for,Blueprint,flash
from flask_login import login_required,current_user

security_bp = Blueprint('security',__name__)

@security_bp.route('/security',methods = ['GET','POST'])
@login_required
def room():
    if current_user.has_fixed_room('security'):
        flash('security is already fixed')
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        submitted_flag = request.form.get('flag','')
        result = flag_validator.validate_flag(current_user,'security',submitted_flag)

        if result['success']:
            flash(result['message'],'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash(result['message'],'danger')
            return redirect(url_for('security.room'))

    return render_template('rooms/security/room.html')

