from flask import Blueprint, render_template
from flask_login import current_user, login_required
from app.models import User

scoreboard_bp = Blueprint('scoreboard', __name__)

@scoreboard_bp.route('/scoreboard')
@login_required
def scoreboard():
    # Sort by total_score DESC and then completion_time ASC
    # Only include users who have officially started the mission
    all_users = User.query.filter(User.start_time != None).order_by(
        User.total_score.desc(),
        User.completion_time.asc()
    ).all()
    return render_template('scoreboard/leaderboard.html', all_users=all_users)