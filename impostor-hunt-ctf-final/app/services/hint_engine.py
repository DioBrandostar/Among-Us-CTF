HINTS = {
    'electrical': [
        "The source code is visible in the browser's developer tools. Check the script section.",
        "Look for a JavaScript variable named 'flag' or something similar inside the main script tag. It's listed right there in the source code!"
    ],
    'cafeteria': [
        "The strange string in the console looks like it's encoded in Base64.",
        "That long string of characters ending in '=' is definitely Base64. Copy it into an online Base64 decoder to see the clear text flag."
    ],
    'medbay': [
        "The URL contains an ID. Try changing it to see other users' scan results.",
        "The suspect's data is at ID 1. Change the `?id=5` in your browser's address bar to `?id=1` and hit enter."
    ],
    'security': [
        "The logs show a lot of noise. Focus on entries that mention 'vent' or 'unauthorized'.",
        "There is a specific log entry that contains a quoted string about 'black' being suspicious. That quoted string is your flag!"
    ],
    'communications': [
        "The server checks your 'role' from a cookie. Check your browser's cookies.",
        "Use your browser's inspect tool (F12) -> Application -> Cookies. Change the value of `crew_role` from `crew` to `admin` and then refresh the page."
    ],
    'reactor': [
        "The password hash is MD5. It's a very common hash that can be easily cracked.",
        "Search for this hash `5f4dcc3b5aa765d61d8327deb882cf99` on a site like CrackStation. It will give you a very common word as the answer."
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
