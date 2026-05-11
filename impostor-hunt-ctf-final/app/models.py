from app.extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    total_score = db.Column(db.Integer, default=0)
    start_time = db.Column(db.DateTime, nullable=True)
    completion_time = db.Column(db.DateTime, nullable=True)  

    all_rooms_fixed = db.Column(db.Boolean, default=False)
    credentials_revealed = db.Column(db.Boolean, default=False)
    impostor_identified = db.Column(db.Boolean, default=False)
    vote_attempts = db.Column(db.Integer, default=0)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_fixed_rooms(self): #Get list of room names this user has fixed
        return [fix.room_name for fix in RoomFix.query.filter_by(user_id=self.id).all()]

    def has_fixed_room(self, room_name): #Check if this user fixed a specific room
        return (
            RoomFix.query.filter_by(user_id=self.id, room_name=room_name).first()
            is not None
        )

    def get_rooms_fixed_count(self): #Count how many rooms fixed
        return RoomFix.query.filter_by(user_id=self.id).count()

    def check_all_rooms_fixed(self): #Check if ALL rooms are fixed
        ALL_ROOMS = [
            'electrical',
            'cafeteria',
            'medbay',
            'security',
            'communications',
            'reactor',
            'admin_terminal'
        ]
        fixed = self.get_fixed_rooms()
        return all(room in fixed for room in ALL_ROOMS)

    def get_elapsed_time(self):
        if not self.start_time:
            return None

        end = self.completion_time or datetime.utcnow()
        delta = end - self.start_time

        total_secs = delta.total_seconds()
        hours = int(total_secs // 3600)
        mins = int((total_secs % 3600) // 60)

        if hours > 0:
            return f"{hours}h {mins}m"
        return f"{mins}m"

    def get_used_hints_count(self, room_name):
        """Returns how many hints the user used for a specific room."""
        return HintUsage.query.filter_by(user_id=self.id, room_name=room_name).count()

    def used_hint(self, room_name, hint_number):
        """Checks if a specific hint was already used."""
        return HintUsage.query.filter_by(
            user_id=self.id, 
            room_name=room_name, 
            hint_number=hint_number
        ).first() is not None

    def get_fixed_rooms_with_points(self):
        """Returns a dictionary mapping room_name to points awarded."""
        fixes = RoomFix.query.filter_by(user_id=self.id).all()
        return {fix.room_name: fix.points for fix in fixes}

    def __repr__(self):
        return f'<User {self.username}>'


class RoomFix(db.Model): 
    __tablename__ = 'room_fixes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    room_name = db.Column(db.String(50), nullable=False)
    fixed_at = db.Column(db.DateTime, default=datetime.utcnow)
    points = db.Column(db.Integer, default=0)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'room_name', name='unique_user_room'),
    )


class FlagSubmission(db.Model):
    __tablename__ = 'flag_submissions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    room_name = db.Column(db.String(50), nullable=False)
    submitted_flag = db.Column(db.String(200), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    points_awarded = db.Column(db.Integer, default=0)  


class HintUsage(db.Model):
    __tablename__ = 'hint_usage'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    room_name = db.Column(db.String(50), nullable=False)
    hint_number = db.Column(db.Integer, nullable=False)
    used_at = db.Column(db.DateTime, default=datetime.utcnow)
    points_lost = db.Column(db.Integer, default=0)  
