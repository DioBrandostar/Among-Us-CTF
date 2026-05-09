from flask import request,redirect,render_template,Blueprint
from flask_login import login_required,current_user

main_bp = Blueprint('main','__name__')
@main_bp.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return render_template('main/home.html')

    @main_bp.route('/briefing')
    @login_required
    def briefing():
        return render_template('main/briefing.html')

    @main_bp.route('/intro')
    def intro():
        return render_template('main/intro.html')