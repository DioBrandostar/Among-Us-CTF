import base64
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import HintUsage
from app.services.scoring import sync_user_score
from app.services import flag_validator
from datetime import datetime

emergency_bp = Blueprint('emergency', __name__)

CORRECT_IMPOSTOR = 'Marwan'
EMERGENCY_HINT_COST = 50
WRONG_VOTE_PENALTY = 50
FAILURE_PENALTY = 100
MAX_VOTE_ATTEMPTS = 3

# Admin credentials (same as in admin_terminal's hidden DB table)
EMERGENCY_ADMIN_USER = 'impostor_admin'
EMERGENCY_ADMIN_PASS = 'vent_crawl_2147'

# Chained vulnerability data for airlock
AIRLOCK_PART1 = 'impostor_ejected_gg'
AIRLOCK_PART2 = 'wp_crewmate'
AIRLOCK_B64_MESSAGE = base64.b64encode(
    f"AIRLOCK_KEY_PART1: {AIRLOCK_PART1} | HINT: The second part of the override code is stored in the airlock maintenance log. Inspect the page source code.".encode()
).decode()


@emergency_bp.route('/emergency-locked')
@login_required
def locked():
    """Redirect when emergency button is pressed but rooms aren't all fixed."""
    flash('🔒 Emergency protocol offline. All ship systems must be repaired before calling an emergency meeting.', 'danger')
    return redirect(url_for('dashboard.index'))


@emergency_bp.route('/emergency-login', methods=['GET', 'POST'])
@login_required
def emergency_login():
    """Admin credential gate before the emergency meeting."""
    if not current_user.check_all_rooms_fixed():
        flash('You must repair all systems first!', 'danger')
        return redirect(url_for('dashboard.index'))

    # If already authenticated, skip to vote
    if current_user.credentials_revealed:
        return redirect(url_for('emergency.vote'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if username == EMERGENCY_ADMIN_USER and password == EMERGENCY_ADMIN_PASS:
            current_user.credentials_revealed = True
            db.session.commit()
            flash('✅ Admin credentials verified. Emergency meeting authorized.', 'success')
            return redirect(url_for('emergency.vote'))
        else:
            flash('❌ Invalid admin credentials. Check the Admin Terminal database for the impostor\'s changed credentials.', 'danger')
            return redirect(url_for('emergency.emergency_login'))

    return render_template('emergency/login.html')


@emergency_bp.route('/vote', methods=['GET', 'POST'])
@login_required
def vote():
    if not current_user.check_all_rooms_fixed():
        flash('You must repair all systems first!', 'danger')
        return redirect(url_for('dashboard.index'))

    if not current_user.credentials_revealed:
        flash('You must enter admin credentials to authorize the emergency meeting.', 'danger')
        return redirect(url_for('emergency.emergency_login'))

    # Already identified impostor — go to ejection
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
            # Wrong vote — penalty
            current_user.vote_attempts += 1
            current_user.total_score = max(0, current_user.total_score - WRONG_VOTE_PENALTY)
            db.session.commit()

            remaining = MAX_VOTE_ATTEMPTS - current_user.vote_attempts

            if current_user.vote_attempts >= MAX_VOTE_ATTEMPTS:
                # 3 strikes — failure
                current_user.total_score = max(0, current_user.total_score - FAILURE_PENALTY)
                current_user.vote_attempts = 0
                db.session.commit()
                return redirect(url_for('emergency.failure'))
            else:
                flash(f'❌ {suspect} is not the impostor. -{WRONG_VOTE_PENALTY} points. {remaining} attempt(s) remaining.', 'danger')
                return redirect(url_for('emergency.vote'))

    # Check if emergency hint was used
    emergency_hint_used = current_user.used_hint('emergency', 1)

    crew = [
        {'name': 'Marwan', 'role': 'Security Officer', 'clue': 'Had access to cameras and logs'},
        {'name': 'Kareem', 'role': 'Engineer', 'clue': 'Found near reactor, but had alibi'},
        {'name': 'Yaseen', 'role': 'Navigation Specialist', 'clue': 'Route deviation detected, but framed'},
        {'name': 'Saleem', 'role': 'Comms Technician', 'clue': 'Transmissions sent, but under orders'},
        {'name': 'Adam', 'role': 'Medical Officer', 'clue': 'Accessed medbay records legitimately'},
        {'name': 'Yousef', 'role': 'Ship Captain', 'clue': 'Has all access, but was in cryo sleep'},
    ]

    return render_template('emergency/vote.html',
                         crew=crew,
                         emergency_hint_used=emergency_hint_used,
                         remaining_attempts=remaining_attempts)


@emergency_bp.route('/emergency-hint', methods=['POST'])
@login_required
def emergency_hint():
    """Buy a hint during the emergency meeting — costs points."""
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
        flash(f'💡 Intel recovered! {EMERGENCY_HINT_COST} points deducted from your score.', 'info')
    else:
        flash('You already used the emergency hint.', 'info')

    return redirect(url_for('emergency.vote'))


@emergency_bp.route('/emergency-failure')
@login_required
def failure():
    """Failure screen after 3 wrong votes."""
    return render_template('emergency/failure.html', penalty=FAILURE_PENALTY + (WRONG_VOTE_PENALTY * MAX_VOTE_ATTEMPTS))


@emergency_bp.route('/trigger-ejection')
@login_required
def trigger_ejection():
    if not current_user.impostor_identified:
        flash('You must identify the impostor first!', 'danger')
        return redirect(url_for('emergency.vote'))

    return render_template('emergency/ejection.html')


@emergency_bp.route('/ejection-room', methods=['GET', 'POST'])
@login_required
def ejection_room():
    """Chained vulnerability room — open the outer ejection door."""
    if not current_user.impostor_identified:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        submitted_flag = request.form.get('flag', '').strip()
        result = flag_validator.validate_flag(current_user, 'final', submitted_flag)
        if result['success']:
            current_user.completion_time = datetime.utcnow()
            from app.models import RoomFix
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
            flash('🎉 <strong style="font-size:1.2rem;">OUTER DOOR OPENED — IMPOSTOR EJECTED!</strong><br>The ship is safe! Final Reward: <span style="color:var(--amber); font-weight:700;">400 Points</span>', 'success')
            return redirect(url_for('emergency.victory'))
        else:
            flash('❌ Wrong override code. The outer door remains sealed. Keep investigating the airlock panel.', 'danger')
            return redirect(url_for('emergency.ejection_room'))

    return render_template('emergency/airlock.html',
                         b64_code=AIRLOCK_B64_MESSAGE,
                         airlock_part2=AIRLOCK_PART2)


@emergency_bp.route('/victory')
@login_required
def victory():
    if not current_user.completion_time:
        return redirect(url_for('dashboard.index'))
    return render_template('emergency/victory.html')