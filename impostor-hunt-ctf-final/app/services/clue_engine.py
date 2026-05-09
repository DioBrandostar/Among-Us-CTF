from app.models import RoomFix

CLUES = {
    'medbay': "🏥 The scan records were altered. Someone was trying to hide their physical symptoms.",
    'admin_terminal': "🖥️ A high-level session was hijacked. The impostor has access to administrative controls.",
    'communications': "📡 Internal logs show a user impersonating an officer to gain trust.",
    'reactor': "☢️ The core stability was compromised using a default password. Someone was lazy or arrogant.",
    'security': "🔐 Surveillance logs show a shadowed figure moving through vents in the late hours.",
    'electrical': "⚡ The power grid was bypassed using a custom script. The impostor knows the station's architecture.",
    'cafeteria': "🍕 An encoded message was found under a table. It points to a rendezvous point near the reactor."
}

def get_unlocked_clues(user):
    """Returns a list of clues unlocked by the user based on fixed rooms."""
    if not user or not user.is_authenticated:
        return []
    
    fixed_rooms = user.get_fixed_rooms()
    unlocked = []
    
    for room, text in CLUES.items():
        if room in fixed_rooms:
            unlocked.append({
                'room': room.replace('_', ' ').title(),
                'text': text
            })
            
    return unlocked
