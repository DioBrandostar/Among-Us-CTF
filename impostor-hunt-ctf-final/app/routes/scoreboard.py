from flask import Blueprint, render_template
from flask_login import current_user, login_required
from app.models import User

scoreboard_bp = Blueprint('scoreboard', __name__)

@scoreboard_bp.route('/scoreboard')
@login_required
def scoreboard():
    # Only show winners — users who have completed the game
    winners = User.query.filter(
        User.completion_time != None
    ).order_by(
        User.total_score.desc(),
        User.completion_time.asc()
    ).all()
    return render_template('scoreboard/leaderboard.html', winners=winners)