from app.models import RoomFix

# 6 clues total — admin_terminal no longer gives a clue
# Each clue points toward Marwan but includes misdirection via Kareem
CLUES = {
    'medbay': "🏥 Patient #7 (Marwan) has impossible vitals — blood type 'QR+', 247% O₂. His records were manually altered. But Kareem was also near Medbay that night...",
    'communications': "📡 Someone spoofed Officer credentials to send fake orders. Marwan's login was used at 03:15, but Kareem's radio was found tuned to a restricted frequency.",
    'reactor': "☢️ Unauthorized commands were executed on the reactor core. Maintenance logs show Marwan had access, though Kareem's engineering badge was swiped nearby at 02:50.",
    'security': "🔐 Surveillance footage was tampered with — metadata hidden in the camera files. Marwan deleted security logs at 03:17, but Kareem reported seeing someone else in the hallway.",
    'electrical': "⚡ The power grid was bypassed at Access Point B-12. Marwan's toolkit was found near the fuse box. However, Kareem claims he was repairing navigation at that time.",
    'cafeteria': "🍕 A coded note was found under table 4: 'Meet at reactor, 0300.' Handwriting analysis is inconclusive — it could be Marwan's or Kareem's."
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
