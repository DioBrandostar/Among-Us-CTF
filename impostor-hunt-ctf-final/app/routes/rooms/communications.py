from app.services import flag_validator
from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_required, current_user

communications_bp = Blueprint('communications', __name__)

@communications_bp.route('/communications', methods=['GET', 'POST'])
@login_required
def room():
    if current_user.has_fixed_room('communications'):
        flash('Communications already solved', 'info')
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        submitted_flag = request.form.get('flag', '')
        result = flag_validator.validate_flag(current_user, 'communications', submitted_flag)
        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash(result['message'], 'danger')
            return redirect(url_for('communications.room'))

    return render_template('rooms/communications/room.html')