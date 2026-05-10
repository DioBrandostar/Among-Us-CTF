import subprocess
import os
import platform
from app.services import flag_validator
from flask import request, redirect, url_for, Blueprint, render_template, flash
from flask_login import login_required, current_user

reactor_bp = Blueprint('reactor', __name__)

@reactor_bp.route('/reactor', methods=['GET', 'POST'])
@login_required
def room():
    if not current_user.start_time:
        return redirect(url_for('main.briefing'))

    is_solved = current_user.has_fixed_room('reactor')
    ping_output = None
    ping_error = None

    if request.method == 'POST':
        action = request.form.get('action', '')

        if action == 'diagnose' and not is_solved:
            # OS Command Injection — intentionally vulnerable
            target = request.form.get('target', '').strip()
            if target:
                try:
                    # Intentionally vulnerable: user input passed directly to shell
                    if platform.system() == 'Windows':
                        cmd = f'ping -n 1 {target}'
                    else:
                        cmd = f'ping -c 1 {target}'

                    result = subprocess.run(
                        cmd,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=10,
                        cwd=os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                    )
                    ping_output = result.stdout + result.stderr
                    if not ping_output.strip():
                        ping_output = "[No output returned]"
                except subprocess.TimeoutExpired:
                    ping_error = "⏱️ Command timed out (10s limit)."
                except Exception as e:
                    ping_error = f"⚠️ Diagnostic error: {str(e)}"
            else:
                ping_error = "⚠️ Please enter a sensor node address."

        elif action == 'submit_flag':
            submitted_flag = request.form.get('flag', '')
            result = flag_validator.validate_flag(current_user, 'reactor', submitted_flag)
            if result['success']:
                flash(result['message'], 'success')
                return redirect(url_for('dashboard.index'))
            else:
                flash(result['message'], 'danger')
                return redirect(url_for('reactor.room'))

    return render_template('rooms/reactor/room.html',
                         is_solved=is_solved,
                         ping_output=ping_output,
                         ping_error=ping_error)