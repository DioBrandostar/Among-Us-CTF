from flask import Blueprint,render_template,request,flash,redirect,url_for
from flask_login import login_required,current_user

emergency_bp = Blueprint('emergency',__name__)

CORRECT_IMPOSTER = 'Red'

ADMIN_USERNAME = 'sysadmin'

@emergency_bp.route('/emergency',methods=['GET','POST'])
@login_required

def vote():
    if current_user.username != ADMIN_USERNAME:
        flash('ACCESS DENIED: Emergency voting is for authorized users only!', 'danger')
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        voted_imposter = request.form.get('imposter')

        if voted_imposter == CORRECT_IMPOSTER:
            flash('Vote Successful! The Impostor has been successfully voted out :)', 'success')
            return redirect(url_for(''))

        else :
            flash('That is not the imposter. The clues point to someone else,try again! ','danger' )
            return redirect(url_for('emergency.vote'))

    return render_template('emergency/vote.html')


