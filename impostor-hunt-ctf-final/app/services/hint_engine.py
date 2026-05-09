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
        "The logs show a lot of noise. Focus on entries that mention 'vent' or 'unauthorized'.",
        "There is a specific log entry that contains a quoted string about 'black' being suspicious. That quoted string is your flag!"
    ],
    'communications': [
        "The radio is receiving a stream of MD5 hashes. One of them is a very common password.",
        "Try cracking the hashes using an online MD5 lookup. Enter the decoded word in the restore field."
    ],
    'reactor': [
        "The password hash is MD5. It's a very common hash that can be easily cracked.",
        "Search for this hash `482c811da5d5b4bc6d497ffa98491e38` on a site like CrackStation. It will give you a very common word as the answer."
    ],
    'admin_terminal': [
        "The search bar doesn't sanitize input. Try injecting a script tag like `<script>alert(1)</script>`.",
        "Try putting `<script>alert(document.cookie)</script>` into the search box. The alert that pops up will show you the session data flag."
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
