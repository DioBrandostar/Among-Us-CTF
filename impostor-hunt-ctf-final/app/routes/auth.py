from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from app.models import User
import traceback
import os

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            user = User.query.filter_by(username=username).first()
            
            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page if next_page else url_for('main.index'))
            else:
                flash('Invalid username or password', 'danger')
        except Exception as e:
            print("Login error:")
            traceback.print_exc()
            flash('An internal server error occurred during login. See terminal for details.', 'danger')
            
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            user = User.query.filter_by(username=username).first()
            
            if user:
                flash('Username already exists', 'danger')
            else:
                new_user = User(
                    username=username,
                    password_hash=generate_password_hash(password)
                )
                db.session.add(new_user)
                db.session.commit()
                
                flash('Registration successful. Please log in.', 'success')
                return redirect(url_for('auth.login'))
        except Exception as e:
            print("Register error:")
            traceback.print_exc()
            flash('An internal server error occurred during registration. See terminal for details.', 'danger')
            
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    try:
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('main.index'))
    except Exception as e:
        print("Logout error:")
        traceback.print_exc()
        flash('An internal server error occurred during logout. See terminal for details.', 'danger')
        return redirect(url_for('main.index'))