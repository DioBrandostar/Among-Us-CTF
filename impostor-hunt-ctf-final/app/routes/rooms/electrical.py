from app.services import flag_validator
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from flask import request, redirect, flash, url_for

electrical_bp = Blueprint('electrical', __name__)

@electrical_bp.route('/electrical', methods=['GET', 'POST'])
@login_required
def room():
    if current_user.has_fixed_room('electrical'):
        flash('Electrical already solved', 'info')
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        submitted_flag = request.form.get('flag', '')
        result = flag_validator.validate_flag(current_user, 'electrical', submitted_flag)
        
        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash(result['message'], 'danger')
            return redirect(url_for('electrical.room'))
            
    return render_template('rooms/electrical/room.html')
