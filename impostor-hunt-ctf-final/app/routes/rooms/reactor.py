from app.services import flag_validator
from flask import request, redirect, url_for, Blueprint, render_template, flash
from flask_login import login_required, current_user

reactor_bp = Blueprint('reactor', __name__)

@reactor_bp.route('/reactor', methods=['GET', 'POST'])
@login_required
def room():
    if not current_user.start_time:
        return redirect(url_for('main.briefing'))
    if current_user.has_fixed_room('reactor'):
        flash('Reactor already fixed', 'info')
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        submitted_flag = request.form.get('flag', '')
        result = flag_validator.validate_flag(current_user, 'reactor', submitted_flag)

        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash(result['message'], 'danger')
            return redirect(url_for('reactor.room'))

    return render_template('rooms/reactor/room.html')