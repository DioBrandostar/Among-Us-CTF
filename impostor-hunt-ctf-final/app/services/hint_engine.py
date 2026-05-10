HINTS = {
    'electrical': [
        "The ship's engineers sometimes leave notes in the system's source code. Try inspecting the page.",
        "Right-click anywhere and select 'View Page Source'. Look for a commented-out line that contains the flag."
    ],
    'cafeteria': [
        "The digital menu display is corrupted with Base64 encoding. Try decoding the items.",
        "Those strange strings on the menu (ending in '=') are Base64. Decode each one — one of them isn't a food name."
    ],
    'medbay': [
        "You're assigned ID #8, but there are 7 other crew members. What if you changed the ID in the URL?",
        "Try changing ?id=8 to other numbers (1-7). Some crew reports have ABNORMAL status with corrupted data containing flag parts."
    ],
    'security': [
        "The recovered surveillance photo may contain more than meets the eye. Have you checked the file's metadata?",
        "Download the photo and inspect its EXIF metadata (use exiftool or an online EXIF viewer). The hidden text is encoded with a Caesar cipher — try different shift values."
    ],
    'communications': [
        "The radio is receiving a stream of MD5 hashes. One of them is a very common password.",
        "Try cracking the hashes using an online MD5 lookup. Enter the decoded word in the restore field."
    ],
    'reactor': [
        "The diagnostic terminal runs system commands. What if the input isn't just an IP address?",
        "Try appending a second command after the address using & or ; — for example: 127.0.0.1 & type flag.txt (Windows) or 127.0.0.1 ; cat flag.txt (Linux)."
    ],
    'admin_terminal': [
        "The crew search doesn't sanitize input. What if you used SQL syntax in the search field?",
        "Try a UNION-based SQL injection: ' UNION SELECT 1,2,3 FROM secrets -- to discover hidden tables and their contents."
    ],
    'emergency': [
        "All sabotaged systems required high-level access — cameras, reactor, admin panel, communications. Only one role has clearance for ALL of these systems."
    ]
}

def get_hint_text(room_name, hint_number):
    """Returns the text for a specific hint in a room."""
    room_hints = HINTS.get(room_name)
    if not room_hints:
        return None
    
    if 1 <= hint_number <= len(room_hints):
        return room_hints[hint_number - 1]
    
    return None
