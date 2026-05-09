from app.services import flag_validator
from flask import request, redirect, url_for, Blueprint, render_template, flash
from flask_login import login_required, current_user

admin_terminal_bp = Blueprint('admin_terminal', __name__)

@admin_terminal_bp.route('/admin_terminal', methods=['GET', 'POST'])   # added methods
@login_required
def room():
    if current_user.has_fixed_room('admin_terminal'):
        flash('admin_terminal is already fixed')
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        submitted_flag = request.form.get('flag')
        result = flag_validator.validate_flag(current_user, 'admin_terminal', submitted_flag)
        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash(result['message'], 'danger')
            return redirect(url_for('admin_terminal.room'))

    return render_template('rooms/admin_terminal/room.html')