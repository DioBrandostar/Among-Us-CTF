import subprocess
import os
import platform
from app.services import flag_validator
from flask import request, redirect, url_for, Blueprint, render_template, flash
from flask_login import login_required, current_user

reactor_bp = Blueprint('reactor', __name__)

# Simulated filesystem for the reactor terminal
SIMULATED_DIR = """
 Volume in drive C is REACTOR-CORE
 Directory of C:\\reactor-systems

05/10/2147  03:22 AM    <DIR>          .
05/10/2147  03:22 AM    <DIR>          ..
05/10/2147  02:15 AM               512  cooldown_override.sh
05/10/2147  01:44 AM             1,024  reactor_core.cfg
05/10/2147  03:18 AM                41  flag.txt
05/10/2147  02:50 AM             2,048  diagnostics.log
05/10/2147  01:00 AM               256  README.txt
               5 File(s)          3,881 bytes
               2 Dir(s)   4,096,000 bytes free
""".strip()

SIMULATED_README = """
[REACTOR MAINTENANCE NOTES]
===========================
The reactor_cooldown command requires Level 5 clearance.
If cooldown fails, use the diagnostic ping tool to check
sensor connectivity. Note: The ping utility has not been
patched since the last security audit.

- Reactor Engineering Team
""".strip()


@reactor_bp.route('/reactor', methods=['GET', 'POST'])
@login_required
def room():
    if not current_user.start_time:
        return redirect(url_for('main.briefing'))

    is_solved = current_user.has_fixed_room('reactor')
    terminal_output = None
    terminal_error = None
    last_command = ''

    if request.method == 'POST':
        action = request.form.get('action', '')

        if action == 'terminal' and not is_solved:
            cmd_input = request.form.get('command', '').strip()
            last_command = cmd_input
            cmd_lower = cmd_input.lower().strip()

            if not cmd_input:
                terminal_error = "⚠️ Please enter a command."

            # Simulated: dir / ls
            elif cmd_lower in ('dir', 'ls', 'dir .', 'ls .', 'ls -la', 'dir /a'):
                terminal_output = SIMULATED_DIR

            # Simulated: type / cat (permission denied)
            elif cmd_lower.startswith('type ') or cmd_lower.startswith('cat '):
                filename = cmd_input.split(None, 1)[1] if len(cmd_input.split(None, 1)) > 1 else ''
                terminal_output = f"Access Denied: Cannot read '{filename}'\nError: Insufficient privileges. Level 5 clearance required.\nContact system administrator for elevated access."

            # Simulated: reactor_cooldown
            elif cmd_lower.startswith('reactor_cooldown'):
                terminal_output = ("ACCESS DENIED: reactor_cooldown requires Level 5 clearance.\n"
                                   "Current user: reactor_tech (Level 2)\n"
                                   "Contact: admin@horizon-7.ship for clearance upgrade.\n"
                                   "STATUS: Command blocked by security policy.")

            # Simulated: help
            elif cmd_lower in ('help', '?', 'help()'):
                terminal_output = ("Available commands:\n"
                                   "  dir / ls          - List directory contents\n"
                                   "  type / cat <file> - Read file contents (requires clearance)\n"
                                   "  ping <address>    - Ping sensor node\n"
                                   "  reactor_cooldown  - Initiate cooldown sequence (Level 5)\n"
                                   "  help              - Show this help message\n"
                                   "  readme            - Read maintenance notes")

            # Simulated: readme
            elif cmd_lower in ('readme', 'type readme.txt', 'cat readme.txt'):
                terminal_output = SIMULATED_README

            # PING — OS Command Injection (intentionally vulnerable)
            elif cmd_lower.startswith('ping '):
                target = cmd_input[5:].strip()
                if target:
                    try:
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
                        terminal_output = result.stdout + result.stderr
                        if not terminal_output.strip():
                            terminal_output = "[No output returned]"
                    except subprocess.TimeoutExpired:
                        terminal_error = "⏱️ Command timed out (10s limit)."
                    except Exception as e:
                        terminal_error = f"⚠️ Diagnostic error: {str(e)}"
                else:
                    terminal_error = "⚠️ Usage: ping <address>"

            else:
                terminal_output = f"'{cmd_input}' is not recognized as a valid command.\nType 'help' for available commands."

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
                         terminal_output=terminal_output,
                         terminal_error=terminal_error,
                         last_command=last_command)