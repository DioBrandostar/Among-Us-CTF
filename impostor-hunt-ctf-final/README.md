# Impostor Hunt CTF

Welcome to the **Impostor Hunt CTF**! This is a beginner-friendly Capture The Flag (CTF) game based on a popular space deduction theme. You will play the role of an investigator trying to uncover the impostor among the crew by solving a series of fun and educational cybersecurity puzzles.

## Getting Started

You do not need to install Python or any dependencies to play this game! It has been packaged into a simple, ready-to-use application.

### How to Play

1. **Locate the Game**: Go to the `dist/ImpostorHunt` folder.
2. **Run the Game**: Double-click the `ImpostorHunt.exe` file.
3. **Keep the Window Open**: A black terminal window will appear. **Do not close this window!** It acts as the game server.
4. **Play in Browser**: Your web browser should automatically open to `http://127.0.0.1:5000`. If it doesn't, simply open your favorite browser and go to that address.

### The Story
You are an investigator aboard the Horizon-7 Space Station. Strange things have been happening, and it's up to you to access the station's systems, gather clues, and find out who the impostor is. Good luck!

---

## 🛠️ For Developers & Organizers

If you want to modify the game, add new challenges, or run it from the source code, follow these steps:

### Prerequisites
* Python 3.8 or higher installed on your system.

### Installation
1. Open your terminal or command prompt in the project folder.
2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the App from Source
To start the Flask development server:
```bash
python run.py
```

### Building the Executable
If you make changes to the code and want to create a new `.exe` file for players to use without installing Python:
1. Ensure your virtual environment is activated and all dependencies are installed.
2. Double-click the `build_exe.bat` file in the main directory.
3. Wait for the process to finish. The new game will be ready in the `dist/ImpostorHunt` folder.