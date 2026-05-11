from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def index():
    if not current_user.start_time:
        return redirect(url_for('main.briefing'))
    fixed_rooms = current_user.get_fixed_rooms_with_points()

    # Only count the 6 core ship systems for progress (not admin_terminal or final)
    CORE_ROOMS = ['electrical', 'cafeteria', 'medbay', 'security', 'communications', 'reactor']
    core_progress = sum(1 for r in fixed_rooms if r in CORE_ROOMS)

    all_done = current_user.check_all_rooms_fixed()

    return render_template('main/dashboard.html', fixed_rooms=fixed_rooms, core_progress=core_progress, all_done=all_done)