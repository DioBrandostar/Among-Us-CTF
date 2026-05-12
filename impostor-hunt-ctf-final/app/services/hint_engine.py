HINTS = {
    'electrical': [
        "Kareem scratches his head: \"The ship's engineers sometimes leave notes in the system's source code. Try inspecting the page — right-click and view source.\"",
        "Kareem sighs: \"Right-click anywhere and select 'View Page Source'. Look for a commented-out line containing the flag. We're not great at hiding things.\""
    ],
    'cafeteria': [
        "Saleem leans in: \"The digital menu display got corrupted with some encoding. Those weird strings ending in '=' look like Base64 to me.\"",
        "Saleem whispers: \"Decode each Base64 string on the menu. One of them isn't a food name — it's something the impostor hid there.\""
    ],
    'medbay': [
        "Adam adjusts his glasses: \"You're assigned patient ID #8, but there are only 7 crew members. What if you changed the ID in the URL to see other records?\"",
        "Adam checks his clipboard: \"Try changing ?id=8 to other numbers (1-7). Some crew reports show ABNORMAL status with corrupted data containing flag fragments.\""
    ],
    'security': [
        "Marwan crosses his arms: \"The recovered surveillance photo contains more than pixels. Have you checked the file's metadata with an EXIF viewer?\"",
        "Marwan mutters: \"Download the photo and inspect its EXIF metadata. The hidden text is Vigenère-encrypted — the keyword might be hiding in the metadata too, disguised as something ordinary.\""
    ],
    'communications': [
        "Saleem taps the radio: \"We're receiving a stream of MD5 hashes on the emergency channel. One of them is a very common password.\"",
        "Saleem points at the screen: \"Try cracking the hashes using an online MD5 lookup tool. Enter the decoded word in the restore field.\""
    ],
    'reactor': [
        "Kareem wipes grease off his hands: \"The terminal accepts commands like 'dir' and 'type'. Try exploring the filesystem. Some commands are blocked, but the ping tool wasn't patched...\"",
        "Kareem lowers his voice: \"Use command injection via ping: try 127.0.0.1 & type flag.txt — the flag you find is Caesar cipher encoded (shift 7). Decode it before submitting.\""
    ],
    'admin_terminal': [
<<<<<<< Updated upstream
        "Yousef scratches his chin: \"The command system seems to talk to a database behind the scenes. I noticed error messages leak through when you type unexpected characters... try a single quote.\"",
        "Yousef whispers: \"If errors show SQL syntax, you could try UNION-based injection to query other tables. The database might have more than just crew_members — look for tables storing credentials and keys.\""
=======
        "Yousef nods: \"The crew search doesn't sanitize input. What if you used SQL syntax in the search field? Try listing all database tables.\"",
        "Yousef points at the screen: \"Try ' UNION SELECT 1,key,value,4,5 FROM secrets -- to find hidden data. Check system_keys for decryption keys.\""
>>>>>>> Stashed changes
    ],
    'emergency': [
        "All sabotaged systems required high-level access — cameras, reactor, admin panel, communications. Only one role has clearance for ALL of these systems."
    ]
}

# Crew members associated with each room for dialogue hints
ROOM_CREW = {
    'electrical': {'name': 'Kareem', 'role': 'Engineer', 'color': '#FF8C42', 'icon': '🔧', 'character_icon': 'character_electrical.png'},
    'cafeteria': {'name': 'Saleem', 'role': 'Comms Technician', 'color': '#3A9B9B', 'icon': '📡', 'character_icon': 'character_cafeteria.png'},
    'communications': {'name': 'Saleem', 'role': 'Comms Technician', 'color': '#3A9B9B', 'icon': '📡', 'character_icon': 'character_communications.png'},
    'medbay': {'name': 'Adam', 'role': 'Medical Officer', 'color': '#4ECB71', 'icon': '🏥', 'character_icon': 'character_medbay.png'},
    'reactor': {'name': 'Kareem', 'role': 'Engineer', 'color': '#FF8C42', 'icon': '🔧', 'character_icon': 'character_reactor.png'},
    'security': {'name': 'Marwan', 'role': 'Security Officer', 'color': '#FF6B6B', 'icon': '🔐', 'character_icon': 'character_security.png'},
    'admin_terminal': {'name': 'Yousef', 'role': 'Ship Captain', 'color': '#F5A623', 'icon': '🚀', 'character_icon': 'character_admin.png'},
}

def get_hint_text(room_name, hint_number):
    """Returns the text for a specific hint in a room."""
    room_hints = HINTS.get(room_name)
    if not room_hints:
        return None

    if 1 <= hint_number <= len(room_hints):
        return room_hints[hint_number - 1]

    return None

def get_room_crew(room_name):
    """Returns the crew member associated with a room."""
    return ROOM_CREW.get(room_name)