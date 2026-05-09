HINTS = {
    'electrical': [
        "The source code is visible in the browser's developer tools. Check the script section.",
        "The flag is hardcoded as a variable in the JavaScript logic. Look for 'const flag' or similar."
    ],
    'cafeteria': [
        "The strange string in the console looks like it's encoded in Base64.",
        "Use a Base64 decoder online or in Python (`base64.b64decode`) to reveal the flag."
    ],
    'medbay': [
        "The URL contains an ID. Try changing it to see other users' scan results.",
        "ID 1 belongs to the suspect. Accessing `/room/medbay/scan?id=1` will reveal their hidden record."
    ],
    'security': [
        "The logs show a lot of noise. Focus on entries that mention 'vent' or 'unauthorized'.",
        "Search for the specific timestamp mentioned in the briefing to find the anomaly."
    ],
    'communications': [
        "The server checks your 'role' from a cookie. Check your browser's cookies.",
        "Change the `crew_role` cookie from `crew` to `admin` and refresh the page."
    ],
    'reactor': [
        "The password hash is MD5. It's a very common hash that can be easily cracked.",
        "The hash `5f4dcc3b5aa765d61d8327deb882cf99` is the MD5 for 'password'. Use it to log in."
    ],
    'admin_terminal': [
        "The search bar doesn't sanitize input. Try injecting a script tag like `<script>alert(1)</script>`.",
        "The goal is to steal the session cookie. Use JavaScript to read `document.cookie`."
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
