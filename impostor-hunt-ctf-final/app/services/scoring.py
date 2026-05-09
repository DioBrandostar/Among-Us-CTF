from app.extensions import db
from app.models import RoomFix, HintUsage

POINTS_PER_ROOM = 100
HINT_1_PENALTY = 20
HINT_2_PENALTY = 30

def calculate_user_score(user):
    """Calculates the total score for a user based on rooms fixed and hints used."""
    if not user:
        return 0
    
    # Points from rooms
    room_points = db.session.query(db.func.sum(RoomFix.points)).filter_by(user_id=user.id).scalar() or 0
    
    # Penalties from hints
    hint_penalties = db.session.query(db.func.sum(HintUsage.points_lost)).filter_by(user_id=user.id).scalar() or 0
    
    return int(room_points - hint_penalties)

def sync_user_score(user):
    """Updates the total_score field in the User model and commits to DB."""
    if not user:
        return
    
    user.total_score = calculate_user_score(user)
    db.session.commit()
