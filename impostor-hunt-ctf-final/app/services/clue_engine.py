from app.models import RoomFix

# 6 clues total — admin_terminal no longer gives a clue
# (it gives persistent SQL access for credential recovery instead)
CLUES = {
    'medbay': "🏥 The scan records were altered. Someone was trying to hide their physical symptoms.",
    'communications': "📡 Internal logs show a user impersonating an officer to gain trust.",
    'reactor': "☢️ The diagnostic terminal was left wide open. Someone ran unauthorized commands on the core systems.",
    'security': "🔐 Surveillance footage was tampered with — hidden data was embedded in the camera snapshots.",
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
