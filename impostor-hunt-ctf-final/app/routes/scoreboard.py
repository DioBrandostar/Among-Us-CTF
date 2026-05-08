from flask import Blueprint,render_template
from flask_login import current_user,login_required
from app.models import User
from sqlalchemy.ext.orderinglist import ordering_list

scoreboard_bp = Blueprint('scoreboard',__name__)

@scoreboard_bp.route('/scoreboard')
@login_required

def scoreboard():
    all_users = User.query.order_by(User.total_score.desc(),User.completion_time.asc()).all()
    return render_template('main/scoreboard.html',all_users=all_users)