from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from datetime import datetime

emergency_bp = Blueprint('emergency', __name__)

ALL_ROOMS = [
    'communications', 'electrical', 'cafeteria',
    'medbay', 'reactor', 'security', 'admin_terminal'
]

CORRECT_IMPOSTOR = 'Marwan'

@emergency_bp.route('/vote', methods=['GET', 'POST'])
@login_required
def vote():
    if not current_user.check_all_rooms_fixed():
        flash('You must repair all 7 systems first!', 'danger')
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        suspect = request.form.get('suspect')
        if suspect == CORRECT_IMPOSTOR:
            current_user.credentials_revealed = True
            db.session.commit()
            flash('✅ CORRECT! Marwan is the impostor. Admin credentials confirmed.', 'success')
            return redirect(url_for('emergency.trigger_ejection'))
        else:
            flash(f'❌ {suspect} is not the impostor. Try again.', 'danger')
            return redirect(url_for('emergency.vote'))

    crew = [
        {'name': 'Marwan', 'role': 'Security Officer', 'clue': 'Had access to cameras and logs'},
        {'name': 'Kareem', 'role': 'Engineer', 'clue': 'Found near reactor, but had alibi'},
        {'name': 'Yaseen', 'role': 'Navigation Specialist', 'clue': 'Route deviation detected, but framed'},
        {'name': 'Saleem', 'role': 'Comms Technician', 'clue': 'Transmissions sent, but under orders'},
        {'name': 'Adam', 'role': 'Medical Officer', 'clue': 'Accessed medbay records legitimately'},
        {'name': 'Yousef', 'role': 'Ship Captain', 'clue': 'Has all access, but was in cryo sleep'},
    ]

    return render_template('emergency/vote.html', crew=crew)


@emergency_bp.route('/trigger-ejection')
@login_required
def trigger_ejection():
    if not current_user.credentials_revealed:
        flash('You must identify the impostor first!', 'danger')
        return redirect(url_for('emergency.vote'))

    flash('🚨 Ejection sequence initiated. Solve the final override to complete!', 'warning')
    return render_template('emergency/ejection.html')


@emergency_bp.route('/final-room', methods=['GET', 'POST'])
@login_required
def final_room():
    if not current_user.credentials_revealed:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        submitted_flag = request.form.get('flag', '').strip()
        if submitted_flag == 'FLAG{impostor_ejected_gg_wp_crewmate}':
            current_user.completion_time = datetime.utcnow()
            
            # Record the final room fix
            from app.models import RoomFix
            final_fix = RoomFix(
                user_id=current_user.id,
                room_name='final',
                points=400,
                fixed_at=datetime.utcnow()
            )
            db.session.add(final_fix)
            
            from app.services.scoring import sync_user_score
            sync_user_score(current_user)
            
            flash('🎉 <strong style="font-size:1.2rem;">IMPOSTOR EJECTED!</strong><br>The ship is safe! Final Reward: <span style="color:var(--amber); font-weight:700;">400 Points</span>', 'success')
            return redirect(url_for('emergency.victory'))
        else:
            flash('❌ Wrong override code. The airlock remains locked!', 'danger')
            return redirect(url_for('emergency.final_room'))

    return render_template('emergency/final_flag.html')


@emergency_bp.route('/victory')
@login_required
def victory():
    if not current_user.completion_time:
        return redirect(url_for('dashboard.index'))
    return render_template('emergency/victory.html')