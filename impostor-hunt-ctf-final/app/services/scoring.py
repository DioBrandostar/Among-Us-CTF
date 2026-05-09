from app.extensions import db
from app.models import RoomFix, HintUsage

POINTS_PER_ROOM = 100
HINT_1_PENALTY = 20
HINT_2_PENALTY = 30

def calculate_user_score(user):
    """Calculates the total score for a user based on rooms fixed."""
    if not user:
        return 0
    
    # Points from rooms (which already have hint penalties subtracted)
    room_points = db.session.query(db.func.sum(RoomFix.points)).filter_by(user_id=user.id).scalar() or 0
    
    return int(room_points)

def sync_user_score(user):
    """Updates the total_score field in the User model and commits to DB."""
    if not user:
        return
    
    user.total_score = calculate_user_score(user)
    db.session.commit()
