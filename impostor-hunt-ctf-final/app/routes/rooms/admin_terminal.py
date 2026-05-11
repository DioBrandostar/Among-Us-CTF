import sqlite3
from flask import request, redirect, url_for, Blueprint, render_template, flash
from flask_login import login_required, current_user
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

admin_terminal_bp = Blueprint('admin_terminal', __name__)

# AES-128-ECB key (16 bytes) — stored in system_keys table for users to find
AES_KEY = b'0r10n9SecretK3y!'

CREW_PASSWORDS = {
    'kareem_eng': 'r3act0r_k33p3r',
    'yaseen_nav': 'st4r_ch4rt_99',
    'saleem_com': 'fr3qu3ncy_7721',
    'adam_med': 'm3d1c_sc4n_ok',
    'yousef_cap': 'c4pt41n_0r10n',
    'marwan_sec': 'w4tch_th3_d00rs',
    'impostor_admin': 'vent_crawl_2147',
}


def _aes_encrypt(plaintext):
    """AES-128-ECB encryption, returns hex string."""
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    padded = pad(plaintext.encode('utf-8'), AES.block_size)
    return cipher.encrypt(padded).hex()


def _get_db():
    """Create an in-memory SQLite database with multiple tables."""
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Table 1: crew_members
    cur.execute('''CREATE TABLE crew_members (
        crew_id TEXT PRIMARY KEY,
        name TEXT,
        role TEXT,
        department TEXT,
        status TEXT,
        last_login TEXT
    )''')
    cur.executemany('INSERT INTO crew_members VALUES (?, ?, ?, ?, ?, ?)', [
        ('CRW-001', 'Kareem', 'Engineer', 'Reactor Bay', 'Active', '2147-10-11 02:45:00'),
        ('CRW-002', 'Yaseen', 'Navigation Specialist', 'Bridge', 'Active', '2147-10-11 03:10:00'),
        ('CRW-003', 'Saleem', 'Comms Technician', 'Communications', 'Active', '2147-10-11 01:30:00'),
        ('CRW-004', 'Adam', 'Medical Officer', 'Medbay', 'Active', '2147-10-11 04:00:00'),
        ('CRW-005', 'Yousef', 'Ship Captain', 'Bridge', 'Active', '2147-10-10 23:00:00'),
        ('CRW-006', 'Marwan', 'Security Officer', 'Security', 'Active', '2147-10-12 03:15:00'),
        ('CRW-007', 'Marwan', 'Maintenance Tech', 'Unknown', 'Suspended', '2147-10-12 03:22:00'),
    ])

    # Table 2: encrypted_credentials — AES-128-ECB encrypted passwords
    cur.execute('''CREATE TABLE encrypted_credentials (
        id INTEGER PRIMARY KEY,
        username TEXT,
        encrypted_password TEXT,
        algorithm TEXT,
        access_level TEXT
    )''')
    for uname, pwd in CREW_PASSWORDS.items():
        enc = _aes_encrypt(pwd)
        level = 'SUPERUSER' if uname == 'impostor_admin' else 'STANDARD'
        cur.execute(
            'INSERT INTO encrypted_credentials (username, encrypted_password, algorithm, access_level) VALUES (?, ?, ?, ?)',
            (uname, enc, 'AES-128-ECB', level),
        )

    # Table 3: system_keys — contains the AES key (found via SQLi)
    cur.execute('''CREATE TABLE system_keys (
        id INTEGER PRIMARY KEY,
        key_name TEXT,
        key_value TEXT,
        purpose TEXT
    )''')
    cur.executemany('INSERT INTO system_keys VALUES (?, ?, ?, ?)', [
        (1, 'AES_MASTER_KEY', AES_KEY.decode(), 'AES-128-ECB encryption key for credential storage'),
        (2, 'VIGENERE_KW', 'HORIZON', 'Cipher keyword for surveillance subsystem'),
        (3, 'HMAC_SALT', 'orion9-2147-salt', 'Hash salt for integrity checks'),
    ])

    # Table 4: access_logs — suspicious activity pointing to Marwan
    cur.execute('''CREATE TABLE access_logs (
        id INTEGER PRIMARY KEY,
        crew_id TEXT,
        action TEXT,
        timestamp TEXT,
        ip_address TEXT
    )''')
    cur.executemany('INSERT INTO access_logs VALUES (?, ?, ?, ?, ?)', [
        (1, 'CRW-006', 'LOGIN', '2147-10-12 03:15:22', '10.0.7.42'),
        (2, 'CRW-006', 'CHANGED_ADMIN_CREDENTIALS', '2147-10-12 03:16:01', '10.0.7.42'),
        (3, 'CRW-006', 'DELETED_SECURITY_LOGS', '2147-10-12 03:17:44', '10.0.7.42'),
        (4, 'CRW-006', 'CREATED_ACCOUNT: impostor_admin', '2147-10-12 03:18:02', '10.0.7.42'),
        (5, 'CRW-005', 'LOGIN', '2147-10-10 23:00:00', '10.0.1.1'),
        (6, 'CRW-001', 'LOGIN', '2147-10-11 02:45:00', '10.0.3.10'),
    ])

    conn.commit()
    return conn


@admin_terminal_bp.route('/admin_terminal', methods=['GET', 'POST'])
@login_required
def room():
    if not current_user.start_time:
        return redirect(url_for('main.briefing'))

    command_input = ''
    command_output = None
    command_error = None
    columns = []

    if request.method == 'POST':
        command_input = request.form.get('command', '').strip()
        if command_input:
            conn = _get_db()
            try:
                # INTENTIONALLY VULNERABLE — raw string format into SQL
                sql = f"SELECT name, role, department, status FROM crew_members WHERE name = '{command_input}'"
                cur = conn.cursor()
                cur.execute(sql)
                columns = [desc[0] for desc in cur.description]
                command_output = [dict(zip(columns, row)) for row in cur.fetchall()]
            except Exception as e:
                command_error = str(e)
            finally:
                conn.close()

    return render_template('rooms/admin_terminal/room.html',
                         command_input=command_input,
                         command_output=command_output,
                         command_error=command_error,
                         columns=columns)