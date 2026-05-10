import os
from app.services import flag_validator
from flask import request, redirect, render_template, url_for, Blueprint, flash, send_from_directory
from flask_login import login_required, current_user

security_bp = Blueprint('security', __name__)

@security_bp.route('/security', methods=['GET', 'POST'])
@login_required
def room():
    if not current_user.start_time:
        return redirect(url_for('main.briefing'))

    is_solved = current_user.has_fixed_room('security')

    if request.method == 'POST' and not is_solved:
        submitted_flag = request.form.get('flag', '')
        result = flag_validator.validate_flag(current_user, 'security', submitted_flag)
        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash(result['message'], 'danger')
            return redirect(url_for('security.room'))

    return render_template('rooms/security/room.html', is_solved=is_solved)


@security_bp.route('/security/download-footage')
@login_required
def download_footage():
    """Serve the surveillance photo with embedded EXIF metadata."""
    images_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static', 'images')
    return send_from_directory(images_dir, 'surveillance_corrupted.jpg', as_attachment=True)
