from app.services import flag_validator
from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_required, current_user

communications_bp = Blueprint('communications', __name__)

@communications_bp.route('/communications', methods=['GET', 'POST'])
@login_required
def room():
    if not current_user.start_time:
        return redirect(url_for('main.briefing'))

    is_solved = current_user.has_fixed_room('communications')
    show_flag = False

    if request.method == 'POST' and not is_solved:
        action = request.form.get('action')

        if action == 'restore':
            code = request.form.get('code', '').strip().lower()
            if code == 'password':
                show_flag = True
                flash('📡 Signal stabilized! Emergency override channel open.', 'success')
            else:
                flash('❌ Invalid restore code. Signal remains unstable.', 'danger')

        elif action == 'submit_flag':
            submitted_flag = request.form.get('flag', '')
            result = flag_validator.validate_flag(current_user, 'communications', submitted_flag)
            if result['success']:
                flash(result['message'], 'success')
                return redirect(url_for('dashboard.index'))
            else:
                flash(result['message'], 'danger')
                show_flag = True

    return render_template('rooms/communications/room.html', is_solved=is_solved, show_flag=show_flag)