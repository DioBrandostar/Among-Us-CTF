import sqlite3
from app.services import flag_validator
from flask import request, redirect, url_for, Blueprint, render_template, flash
from flask_login import login_required, current_user

admin_terminal_bp = Blueprint('admin_terminal', __name__)


def _get_db():
    """Create an in-memory SQLite database with intentionally vulnerable data."""
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Crew logs table — visible to normal queries
    cur.execute('''CREATE TABLE crew_logs (
        id INTEGER PRIMARY KEY,
        name TEXT,
        role TEXT,
        last_seen TEXT
    )''')
    cur.executemany('INSERT INTO crew_logs (name, role, last_seen) VALUES (?, ?, ?)', [
        ('Kareem', 'Engineer', 'Reactor Bay — 02:45'),
        ('Yaseen', 'Navigation Specialist', 'Bridge — 03:10'),
        ('Saleem', 'Comms Technician', 'Communications — 01:30'),
        ('Adam', 'Medical Officer', 'Medbay — 04:00'),
        ('Yousef', 'Ship Captain', 'Cryo Chamber — 00:00'),
        ('Marwan', 'Security Officer', 'Unknown — last seen 03:15'),
    ])

    # Secrets table — contains the flag (hidden, discoverable via SQL injection)
    cur.execute('''CREATE TABLE secrets (
        id INTEGER PRIMARY KEY,
        key TEXT,
        value TEXT
    )''')
    cur.execute("INSERT INTO secrets (key, value) VALUES (?, ?)",
                ('system_flag', 'FLAG{sql_injection_admin_pwned}'))
    cur.execute("INSERT INTO secrets (key, value) VALUES (?, ?)",
                ('backup_code', 'ORION-9-FAILSAFE-7742'))

    # Admin credentials table — impostor's changed credentials (for post-fix discovery)
    cur.execute('''CREATE TABLE admin_credentials (
        id INTEGER PRIMARY KEY,
        username TEXT,
        password TEXT,
        access_level TEXT
    )''')
    cur.execute("INSERT INTO admin_credentials (username, password, access_level) VALUES (?, ?, ?)",
                ('impostor_admin', 'vent_crawl_2147', 'SUPERUSER'))

    conn.commit()
    return conn


@admin_terminal_bp.route('/admin_terminal', methods=['GET', 'POST'])
@login_required
def room():
    if not current_user.start_time:
        return redirect(url_for('main.briefing'))

    is_solved = current_user.has_fixed_room('admin_terminal')
    search_results = None
    search_query = ''
    search_error = None
    columns = []

    if request.method == 'POST':
        action = request.form.get('action', '')

        if action == 'search':
            search_query = request.form.get('query', '').strip()
            if search_query:
                conn = _get_db()
                try:
                    # INTENTIONALLY VULNERABLE — raw string format, no parameterization
                    sql = f"SELECT id, name, role, last_seen FROM crew_logs WHERE name LIKE '%{search_query}%'"
                    cur = conn.cursor()
                    cur.execute(sql)
                    columns = [desc[0] for desc in cur.description]
                    search_results = [dict(zip(columns, row)) for row in cur.fetchall()]
                except Exception as e:
                    search_error = str(e)
                finally:
                    conn.close()

        elif action == 'submit_flag' and not is_solved:
            submitted_flag = request.form.get('flag', '')
            result = flag_validator.validate_flag(current_user, 'admin_terminal', submitted_flag)
            if result['success']:
                flash(result['message'], 'success')
                return redirect(url_for('dashboard.index'))
            else:
                flash(result['message'], 'danger')
                return redirect(url_for('admin_terminal.room'))

    return render_template('rooms/admin_terminal/room.html',
                         is_solved=is_solved,
                         search_results=search_results,
                         search_query=search_query,
                         search_error=search_error,
                         columns=columns)