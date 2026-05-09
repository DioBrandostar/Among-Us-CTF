from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.models import HintUsage
from app.extensions import db
from app.services.hint_engine import get_hint_text
from app.services.scoring import sync_user_score, HINT_1_PENALTY, HINT_2_PENALTY

from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return render_template('main/home.html')

@main_bp.route('/briefing')
@login_required
def briefing():
    if current_user.start_time:
        return redirect(url_for('dashboard.index'))
    return render_template('main/briefing.html')

@main_bp.route('/start-mission', methods=['POST'])
@login_required
def start_mission():
    if not current_user.start_time:
        current_user.start_time = datetime.utcnow()
        db.session.commit()
        flash("Mission started. Good luck, investigator.", "success")
    return redirect(url_for('dashboard.index'))

@main_bp.route('/hint/<room_name>', methods=['POST'])
@login_required
def get_hint(room_name):
    # Determine which hint to give
    hints_used = current_user.get_used_hints_count(room_name)
    next_hint_num = hints_used + 1
    
    hint_text = get_hint_text(room_name, next_hint_num)
    
    if not hint_text:
        flash("No more hints available for this room.", "info")
        return redirect(url_for(f'{room_name}.room'))
    
    # Check if already used
    if not current_user.used_hint(room_name, next_hint_num):
        penalty = HINT_1_PENALTY if next_hint_num == 1 else HINT_2_PENALTY
        
        new_hint = HintUsage(
            user_id=current_user.id,
            room_name=room_name,
            hint_number=next_hint_num,
            points_lost=penalty
        )
        db.session.add(new_hint)
        db.session.commit()
        flash(f"Hint revealed! The room's value has decreased by {penalty} points.", "warning")
    
    return redirect(url_for(f'{room_name}.room'))