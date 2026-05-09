from app.services import flag_validator
from flask import request, redirect, url_for, flash, Blueprint, render_template
from flask_login import login_required, current_user

medbay_bp = Blueprint('medbay', __name__)

# Crew medical records — 8 total (7 crew + user at id=8)
# IDs 2, 5, 7 have corrupted reports containing flag parts
CREW_RECORDS = {
    1: {
        'name': 'Captain Reyes',
        'role': 'Navigation Officer',
        'blood_type': 'O+',
        'heart_rate': '72 bpm',
        'status': 'HEALTHY',
        'notes': 'No anomalies detected. Cleared for active duty.',
        'corrupted': False,
    },
    2: {
        'name': 'Dr. Vasquez',
        'role': 'Chief Medical Officer',
        'blood_type': 'A-',
        'heart_rate': '68 bpm',
        'status': 'ABNORMAL',
        'notes': 'Brain scan corrupted. Embedded data recovered: FLAG{idor',
        'corrupted': True,
    },
    3: {
        'name': 'Engineer Tanaka',
        'role': 'Systems Engineer',
        'blood_type': 'B+',
        'heart_rate': '75 bpm',
        'status': 'HEALTHY',
        'notes': 'Minor radiation exposure within safe limits. Cleared.',
        'corrupted': False,
    },
    4: {
        'name': 'Officer Blake',
        'role': 'Security Officer',
        'blood_type': 'AB+',
        'heart_rate': '80 bpm',
        'status': 'HEALTHY',
        'notes': 'Elevated stress hormones. Recommended for psych eval.',
        'corrupted': False,
    },
    5: {
        'name': 'Tech Specialist Orion',
        'role': 'Communications Tech',
        'blood_type': 'O-',
        'heart_rate': '65 bpm',
        'status': 'ABNORMAL',
        'notes': 'DNA scan file corrupted. Embedded data recovered: _body_',
        'corrupted': True,
    },
    6: {
        'name': 'Navigator Patel',
        'role': 'Astro-Navigator',
        'blood_type': 'A+',
        'heart_rate': '70 bpm',
        'status': 'HEALTHY',
        'notes': 'All vitals nominal. Sleep pattern irregular but non-critical.',
        'corrupted': False,
    },
    7: {
        'name': 'Marwan',
        'role': 'Maintenance Crew',
        'blood_type': 'B-',
        'heart_rate': '??? bpm',
        'status': 'ABNORMAL',
        'notes': 'Medical scan file corrupted. Embedded data recovered: reported}',
        'corrupted': True,
    },
}

# Clean records shown when solved
CLEAN_NOTES = {
    2: 'Brain scan normal. No anomalies. Cleared for duty.',
    5: 'DNA scan normal. All markers within expected range.',
    7: 'Medical scan complete. All vitals within normal parameters.',
}


@medbay_bp.route('/medbay', methods=['GET', 'POST'])
@login_required
def room():
    if not current_user.start_time:
        return redirect(url_for('main.briefing'))

    is_solved = current_user.has_fixed_room('medbay')

    if request.method == 'POST' and not is_solved:
        submitted_flag = request.form.get('flag', '')
        result = flag_validator.validate_flag(current_user, 'medbay', submitted_flag)
        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash(result['message'], 'danger')
            return redirect(url_for('medbay.room'))

    # Get which crew record to view
    view_id = request.args.get('id', None, type=int)
    viewed_record = None

    if view_id and view_id in CREW_RECORDS:
        record = CREW_RECORDS[view_id].copy()
        # If solved, replace corrupted notes with clean versions
        if is_solved and view_id in CLEAN_NOTES:
            record['notes'] = CLEAN_NOTES[view_id]
            record['status'] = 'HEALTHY'
        viewed_record = record
        viewed_record['id'] = view_id

    # User's own record (id=8)
    user_record = {
        'name': current_user.username,
        'role': 'Investigator',
        'blood_type': 'A+',
        'heart_rate': '74 bpm',
        'status': 'HEALTHY',
        'notes': 'All vitals nominal. Cleared for investigation duty.',
    }

    return render_template('rooms/medbay/room.html',
                         is_solved=is_solved,
                         crew_records=CREW_RECORDS,
                         viewed_record=viewed_record,
                         view_id=view_id,
                         user_record=user_record)
