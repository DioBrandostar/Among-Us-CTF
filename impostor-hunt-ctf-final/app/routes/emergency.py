import base64
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models import HintUsage, RoomFix
from app.services.scoring import sync_user_score
from datetime import datetime

emergency_bp = Blueprint('emergency', __name__)

CORRECT_IMPOSTOR = 'Marwan'
EMERGENCY_HINT_COST = 50
EMERGENCY_LOGIN_HINT_COST = 30
WRONG_VOTE_PENALTY = 50
FAILURE_PENALTY = 100
MAX_VOTE_ATTEMPTS = 3

# Admin credentials (found via SQLi + AES decryption in admin_terminal)
EMERGENCY_ADMIN_USER = 'impostor_admin'
EMERGENCY_ADMIN_PASS = 'vent_crawl_2147'


@emergency_bp.route('/emergency-locked')
@login_required
def locked():
    flash('🔒 Emergency protocol offline. All ship systems must be repaired before calling an emergency meeting.', 'danger')
    return redirect(url_for('dashboard.index'))


@emergency_bp.route('/emergency-login', methods=['GET', 'POST'])
@login_required
def emergency_login():
    if not current_user.check_all_rooms_fixed():
        flash('You must repair all systems first!', 'danger')
        return redirect(url_for('dashboard.index'))

    if current_user.credentials_revealed:
        return redirect(url_for('emergency.vote'))

    login_hint_used = current_user.used_hint('emergency_login', 1)

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if username == EMERGENCY_ADMIN_USER and password == EMERGENCY_ADMIN_PASS:
            current_user.credentials_revealed = True
            db.session.commit()
            flash('✅ Admin credentials verified. Emergency meeting authorized.', 'success')
            return redirect(url_for('emergency.vote'))
        else:
            flash('❌ Invalid admin credentials. Investigate the Admin Terminal database to find them.', 'danger')
            return redirect(url_for('emergency.emergency_login'))

    return render_template('emergency/login.html', login_hint_used=login_hint_used)


@emergency_bp.route('/emergency-login-hint', methods=['POST'])
@login_required
def emergency_login_hint():
    if not current_user.used_hint('emergency_login', 1):
        new_hint = HintUsage(
            user_id=current_user.id,
            room_name='emergency_login',
            hint_number=1,
            points_lost=EMERGENCY_LOGIN_HINT_COST
        )
        db.session.add(new_hint)
        current_user.total_score = max(0, current_user.total_score - EMERGENCY_LOGIN_HINT_COST)
        db.session.commit()
        flash(f'💡 Intel recovered! -{EMERGENCY_LOGIN_HINT_COST} points.', 'info')
    else:
        flash('You already purchased this intel.', 'info')
    return redirect(url_for('emergency.emergency_login'))


@emergency_bp.route('/vote', methods=['GET', 'POST'])
@login_required
def vote():
    if not current_user.check_all_rooms_fixed():
        flash('You must repair all systems first!', 'danger')
        return redirect(url_for('dashboard.index'))

    if not current_user.credentials_revealed:
        flash('You must enter admin credentials to authorize the emergency meeting.', 'danger')
        return redirect(url_for('emergency.emergency_login'))

    if current_user.impostor_identified:
        return redirect(url_for('emergency.trigger_ejection'))

    remaining_attempts = MAX_VOTE_ATTEMPTS - current_user.vote_attempts

    if request.method == 'POST':
        suspect = request.form.get('suspect')

        if suspect == CORRECT_IMPOSTOR:
            current_user.impostor_identified = True
            current_user.vote_attempts = 0
            db.session.commit()
            flash('✅ CORRECT! Marwan is the impostor! Initiating ejection sequence...', 'success')
            return redirect(url_for('emergency.trigger_ejection'))
        else:
            current_user.vote_attempts += 1
            current_user.total_score = max(0, current_user.total_score - WRONG_VOTE_PENALTY)
            db.session.commit()

            remaining = MAX_VOTE_ATTEMPTS - current_user.vote_attempts

            if current_user.vote_attempts >= MAX_VOTE_ATTEMPTS:
                current_user.total_score = max(0, current_user.total_score - FAILURE_PENALTY)
                current_user.vote_attempts = 0
                db.session.commit()
                return redirect(url_for('emergency.failure'))
            else:
                flash(f'❌ {suspect} is not the impostor. -{WRONG_VOTE_PENALTY} points. {remaining} attempt(s) remaining.', 'danger')
                return redirect(url_for('emergency.vote'))

    emergency_hint_used = current_user.used_hint('emergency', 1)

    crew = [
        {'name': 'Marwan', 'role': 'Security Officer', 'color': '#FF6B6B', 'clue': 'Had access to cameras and logs'},
        {'name': 'Kareem', 'role': 'Engineer', 'color': '#FF8C42', 'clue': 'Found near reactor, but had alibi'},
        {'name': 'Yaseen', 'role': 'Navigation Specialist', 'color': '#4A90D9', 'clue': 'Route deviation detected, but framed'},
        {'name': 'Saleem', 'role': 'Comms Technician', 'color': '#3A9B9B', 'clue': 'Transmissions sent, but under orders'},
        {'name': 'Adam', 'role': 'Medical Officer', 'color': '#4ECB71', 'clue': 'Accessed medbay records legitimately'},
        {'name': 'Yousef', 'role': 'Ship Captain', 'color': '#F5A623', 'clue': 'Has all access, but was in cryo sleep'},
    ]

    return render_template('emergency/vote.html',
                         crew=crew,
                         emergency_hint_used=emergency_hint_used,
                         remaining_attempts=remaining_attempts)


@emergency_bp.route('/emergency-hint', methods=['POST'])
@login_required
def emergency_hint():
    if not current_user.check_all_rooms_fixed():
        flash('You must repair all systems first!', 'danger')
        return redirect(url_for('dashboard.index'))

    if not current_user.used_hint('emergency', 1):
        new_hint = HintUsage(
            user_id=current_user.id,
            room_name='emergency',
            hint_number=1,
            points_lost=EMERGENCY_HINT_COST
        )
        db.session.add(new_hint)
        current_user.total_score = max(0, current_user.total_score - EMERGENCY_HINT_COST)
        db.session.commit()
        flash(f'💡 Intel recovered! {EMERGENCY_HINT_COST} points deducted.', 'info')
    else:
        flash('You already used the emergency hint.', 'info')

    return redirect(url_for('emergency.vote'))


@emergency_bp.route('/emergency-failure')
@login_required
def failure():
    return render_template('emergency/failure.html',
                         penalty=FAILURE_PENALTY + (WRONG_VOTE_PENALTY * MAX_VOTE_ATTEMPTS))


@emergency_bp.route('/trigger-ejection')
@login_required
def trigger_ejection():
    if not current_user.impostor_identified:
        flash('You must identify the impostor first!', 'danger')
        return redirect(url_for('emergency.vote'))
    return render_template('emergency/ejection.html')


@emergency_bp.route('/ejection-room')
@login_required
def ejection_room():
    if not current_user.impostor_identified:
        return redirect(url_for('dashboard.index'))
    return render_template('emergency/airlock.html')


@emergency_bp.route('/api/airlock-status')
@login_required
def airlock_status():
    """Simulated WebSocket-like endpoint — returns airlock JSON status."""
    if not current_user.impostor_identified:
        return jsonify({"error": "unauthorized"}), 403

    return jsonify({
        "system": "AIRLOCK-CTRL-v1.0",
        "inner_door": "sealed",
        "outer_door": "closed",
        "door_status": "closed",
        "override": False,
        "impostor": "Marwan",
        "chamber_pressure": "0.0 kPa",
        "timestamp": datetime.utcnow().isoformat()
    })


@emergency_bp.route('/api/airlock-override', methods=['POST'])
@login_required
def airlock_override():
    """Player sends modified JSON to open the outer door."""
    if not current_user.impostor_identified:
        return jsonify({"error": "unauthorized"}), 403

    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "invalid JSON", "door_status": "closed"}), 400

    door_status = data.get('door_status', '').lower()
    override = data.get('override', False)

    if door_status == 'opened' or override == True or override == 'true':
        # Success! Mark game complete
        if not current_user.completion_time:
            current_user.completion_time = datetime.utcnow()
            existing = RoomFix.query.filter_by(user_id=current_user.id, room_name='final').first()
            if not existing:
                final_fix = RoomFix(
                    user_id=current_user.id,
                    room_name='final',
                    points=400,
                    fixed_at=datetime.utcnow()
                )
                db.session.add(final_fix)
            sync_user_score(current_user)

        return jsonify({
            "status": "SUCCESS",
            "door_status": "opened",
            "message": "OUTER DOOR OPENED — IMPOSTOR EJECTED INTO SPACE",
            "redirect": url_for('emergency.victory')
        })
    else:
        return jsonify({
            "status": "DENIED",
            "door_status": "closed",
            "message": "Override rejected. Send correct parameters.",
            "hint": "Try changing door_status or override values"
        }), 403


@emergency_bp.route('/victory')
@login_required
def victory():
    if not current_user.completion_time:
        return redirect(url_for('dashboard.index'))
    return render_template('emergency/victory.html')