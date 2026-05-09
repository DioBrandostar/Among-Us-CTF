from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def index():
    if not current_user.start_time:
        return redirect(url_for('main.briefing'))
    fixed_rooms = current_user.get_fixed_rooms_with_points()

    progress_count = current_user.get_rooms_fixed_count()

    all_done = current_user.check_all_rooms_fixed()

    return render_template('main/dashboard.html',fixed_rooms=fixed_rooms,progress_count=progress_count,all_done=all_done)