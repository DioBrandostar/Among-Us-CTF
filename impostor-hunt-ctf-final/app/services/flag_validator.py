from app.extensions import db
from app.models import RoomFix, FlagSubmission
from datetime import datetime

ROOM_FLAGS = {
    'electrical':     'FLAG{lights_out_in_electrical}',
    'cafeteria':      'FLAG{space_food_is_sus}',
    'medbay':         'FLAG{idor_body_reported}',
    'security':       'FLAG{sus_black_was_here}',
    'communications': 'FLAG{cookies_are_not_safe_in_space}',
    'reactor':        'FLAG{hash_cracked_reactor_saved}',
    'admin_terminal': 'FLAG{xss_script_injected_in_space}',
    'final':          'FLAG{impostor_ejected_gg_wp_crewmate}',
}

ROOM_POINTS = {
    'electrical':     50,
    'cafeteria':      50,
    'medbay':         100,
    'security':       100,
    'communications': 150,
    'reactor':        150,
    'admin_terminal': 150,
    'final':          400,
}

ALL_ROOM_IDS = [
    'electrical', 'cafeteria', 'medbay', 'security', 'communications', 'reactor', 'admin_terminal'
]


def validate_flag(user, room_name, submitted_flag):
    submitted_flag = submitted_flag.strip()
    
    # Already solved
    if room_name != 'final' and user.has_fixed_room(room_name):
        return {
            'success':        False,
            'already_solved': True,
            'message':        '✅ You already fixed this room!',
            'points':         0,
            'all_fixed':      user.all_rooms_fixed,
            'redirect':       f'/room/{room_name}'
        }
    
    #Valid room
    correct_flag = ROOM_FLAGS.get(room_name)
    if not correct_flag:
        return {
            'success':        False,
            'already_solved': False,
            'message':        '⚠️ Unknown room.',
            'points':         0,
            'all_fixed':      False,
            'redirect':       '/station'
        }
    
    submission = FlagSubmission(
        user_id        = user.id,
        room_name      = room_name,
        submitted_flag = submitted_flag,
        is_correct     = (submitted_flag == correct_flag),
        timestamp      = datetime.utcnow(),
        points_awarded = 0
    )
    
    if submitted_flag != correct_flag:
        db.session.add(submission)
        db.session.commit()
        return {
            'success':        False,
            'already_solved': False,
            'message':        '❌ Wrong flag. Keep investigating, crewmate!',
            'points':         0,
            'all_fixed':      user.all_rooms_fixed,
            'redirect':       None
        }
    
    points = ROOM_POINTS.get(room_name, 0)
    
    # Subtract hint penalties for this specific room
    from app.models import HintUsage
    hint_penalties = db.session.query(db.func.sum(HintUsage.points_lost)).filter_by(
        user_id=user.id, 
        room_name=room_name
    ).scalar() or 0
    
    final_room_points = max(0, points - hint_penalties)
    
    submission.is_correct     = True
    submission.points_awarded = final_room_points
    db.session.add(submission)
    
    if room_name != 'final':
        fix = RoomFix(
            user_id   = user.id,
            room_name = room_name,
            points    = final_room_points,
            fixed_at  = datetime.utcnow()
        )
        db.session.add(fix)
    
    # Sync score accounting for hints
    from app.services.scoring import sync_user_score
    sync_user_score(user)
    
    if room_name == 'final':
        user.completion_time = datetime.utcnow()
    db.session.commit()
    
    if room_name != 'final':
        fixed_rooms = [
            fix.room_name
            for fix in RoomFix.query.filter_by(user_id=user.id).all()
        ]
        all_done = all(room in fixed_rooms for room in ALL_ROOM_IDS)
        
        if all_done:
            user.all_rooms_fixed      = True
            user.credentials_revealed = True
            db.session.commit()
    
    return {
        'success':        True,
        'already_solved': False,
        'message':        f'🎉 Correct! Room fixed! +{points} points!',
        'points':         points,
        'all_fixed':      user.all_rooms_fixed,
        'redirect':       f'/room/{room_name}'
    }