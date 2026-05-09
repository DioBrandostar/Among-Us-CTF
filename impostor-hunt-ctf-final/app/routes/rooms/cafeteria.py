from app.services import flag_validator
from flask import render_template,url_for,request,redirect,Blueprint,flash
from flask_login import login_required,current_user

cafeteria_bp = Blueprint('cafeteria',__name__)

@cafeteria_bp.route('/cafeteria', methods=['GET', 'POST'])
@login_required
def room():
    if not current_user.start_time:
        return redirect(url_for('main.briefing'))
    if current_user.has_fixed_room('cafeteria'):
        flash('cafeteria already solved')
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        submitted_flag = request.form.get('flag','')
        result = flag_validator.validate_flag(current_user,'cafeteria',submitted_flag )
        if result['success']:
           flash(result['message'],'success')
           return redirect(url_for('dashboard.index'))
        else:
           flash( result['message'],'danger')
           return redirect(url_for('cafeteria.room'))
    return render_template('rooms/cafeteria/room.html')

