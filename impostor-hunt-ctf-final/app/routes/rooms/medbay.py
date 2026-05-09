from app.services import flag_validator
from flask import request, redirect, url_for, flash, Blueprint, render_template
from flask_login import login_required, current_user

medbay_bp = Blueprint('medbay', __name__)

# Crew medical records — 8 total (7 crew + user at id=8)
# IDs 2, 5, 7 have corrupted/abnormal data containing flag parts
CREW_RECORDS = {
    1: {
        'name': 'Captain Reyes',
        'role': 'Navigation Officer',
        'blood_type': 'O+',
        'heart_rate': '72 bpm',
        'blood_pressure': '120/80 mmHg',
        'oxygen_sat': '98%',
        'body_temp': '36.6°C',
        'white_blood_cells': '6,200 /μL',
        'notes': 'All vitals nominal. Cleared for active duty. Last physical: 2147-09-28.',
        'has_error': False,
        'error_fields': [],
    },
    2: {
        'name': 'Dr. Vasquez',
        'role': 'Chief Medical Officer',
        'blood_type': 'Z-',
        'heart_rate': '312 bpm',
        'blood_pressure': '290/180 mmHg',
        'oxygen_sat': '14%',
        'body_temp': '36.8°C',
        'white_blood_cells': '5,800 /μL',
        'notes': 'SYSTEM ERROR: Blood type "Z-" not recognized in database. Heart rate exceeds sensor maximum (250 bpm). Embedded fragment recovered from corrupted scan: FLAG{idor',
        'has_error': True,
        'error_fields': ['blood_type', 'heart_rate', 'blood_pressure', 'oxygen_sat'],
    },
    3: {
        'name': 'Engineer Tanaka',
        'role': 'Systems Engineer',
        'blood_type': 'B+',
        'heart_rate': '75 bpm',
        'blood_pressure': '118/76 mmHg',
        'oxygen_sat': '97%',
        'body_temp': '36.5°C',
        'white_blood_cells': '7,100 /μL',
        'notes': 'Minor radiation exposure within safe limits (0.12 mSv). Cleared for engine maintenance. Noted: was near Reactor during sabotage window.',
        'has_error': False,
        'error_fields': [],
    },
    4: {
        'name': 'Officer Blake',
        'role': 'Security Chief',
        'blood_type': 'AB+',
        'heart_rate': '80 bpm',
        'blood_pressure': '130/85 mmHg',
        'oxygen_sat': '99%',
        'body_temp': '36.7°C',
        'white_blood_cells': '5,500 /μL',
        'notes': 'Elevated cortisol levels consistent with stress. Recommended for psych eval. Reported seeing M████ near electrical at 03:00.',
        'has_error': False,
        'error_fields': [],
    },
    5: {
        'name': 'Tech Specialist Orion',
        'role': 'Communications Tech',
        'blood_type': 'XX',
        'heart_rate': '0 bpm',
        'blood_pressure': '0/0 mmHg',
        'oxygen_sat': '0%',
        'body_temp': '-273.15°C',
        'white_blood_cells': '0 /μL',
        'notes': 'SYSTEM ERROR: All readings return NULL/zero. Sensor calibration failed. Possible hardware tamper. Corrupted data fragment found: _body_',
        'has_error': True,
        'error_fields': ['blood_type', 'heart_rate', 'blood_pressure', 'oxygen_sat', 'body_temp', 'white_blood_cells'],
    },
    6: {
        'name': 'Navigator Patel',
        'role': 'Astro-Navigator',
        'blood_type': 'A+',
        'heart_rate': '70 bpm',
        'blood_pressure': '115/74 mmHg',
        'oxygen_sat': '98%',
        'body_temp': '36.4°C',
        'white_blood_cells': '6,900 /μL',
        'notes': 'All vitals nominal. Sleep pattern irregular but non-critical. Mentioned hearing strange noises from maintenance bay at night.',
        'has_error': False,
        'error_fields': [],
    },
    7: {
        'name': 'Marwan',
        'role': 'Maintenance Crew',
        'blood_type': 'QR+',
        'heart_rate': '999 bpm',
        'blood_pressure': 'ERR/ERR mmHg',
        'oxygen_sat': '247%',
        'body_temp': '89.3°C',
        'white_blood_cells': '98,000 /μL',
        'notes': 'CRITICAL SYSTEM ERROR: Blood type "QR+" does not exist in human database. O2 saturation exceeds 100% (impossible). Temperature incompatible with life. Record appears to have been manually altered. Corrupted data fragment recovered: reported}',
        'has_error': True,
        'error_fields': ['blood_type', 'heart_rate', 'blood_pressure', 'oxygen_sat', 'body_temp', 'white_blood_cells'],
    },
}

# Clean records shown when solved
CLEAN_RECORDS = {
    2: {
        'blood_type': 'A-',
        'heart_rate': '68 bpm',
        'blood_pressure': '122/78 mmHg',
        'oxygen_sat': '97%',
        'notes': 'Brain scan normal. No anomalies. Cleared for duty.',
    },
    5: {
        'blood_type': 'O-',
        'heart_rate': '65 bpm',
        'blood_pressure': '110/70 mmHg',
        'oxygen_sat': '99%',
        'body_temp': '36.3°C',
        'white_blood_cells': '6,400 /μL',
        'notes': 'DNA scan normal. All markers within expected range.',
    },
    7: {
        'blood_type': 'B-',
        'heart_rate': '78 bpm',
        'blood_pressure': '125/82 mmHg',
        'oxygen_sat': '96%',
        'body_temp': '36.9°C',
        'white_blood_cells': '7,200 /μL',
        'notes': 'Medical scan complete. All vitals within normal parameters.',
    },
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

    # Get which crew record to view — defaults to 8 (user)
    view_id = request.args.get('id', 8, type=int)
    viewed_record = None

    if view_id in CREW_RECORDS:
        record = CREW_RECORDS[view_id].copy()
        # If solved, replace corrupted data with clean versions
        if is_solved and view_id in CLEAN_RECORDS:
            clean = CLEAN_RECORDS[view_id]
            for key, val in clean.items():
                record[key] = val
            record['has_error'] = False
            record['error_fields'] = []
        viewed_record = record
        viewed_record['id'] = view_id

    # User's own record (id=8)
    user_record = {
        'name': current_user.username,
        'role': 'Investigator',
        'blood_type': 'A+',
        'heart_rate': '74 bpm',
        'blood_pressure': '118/76 mmHg',
        'oxygen_sat': '98%',
        'body_temp': '36.5°C',
        'white_blood_cells': '6,600 /μL',
        'notes': 'All vitals nominal. Cleared for investigation duty. Last physical: 2147-10-10.',
        'has_error': False,
        'error_fields': [],
    }

    return render_template('rooms/medbay/room.html',
                         is_solved=is_solved,
                         crew_records=CREW_RECORDS,
                         viewed_record=viewed_record,
                         view_id=view_id,
                         user_record=user_record)
