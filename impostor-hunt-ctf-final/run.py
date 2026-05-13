import sys
import traceback

try:
    import os
    import threading
    import webbrowser
    import logging
    
    from app import create_app

    def open_browser():
        """Opens the browser automatically after a short delay."""
        try:
            webbrowser.open_new("http://127.0.0.1:5000")
        except Exception:
            pass

    app = create_app()

    if __name__ == '__main__':
        port = int(os.environ.get('PORT', 5000))
        
        # Determine if we are running as a PyInstaller executable
        is_exe = getattr(sys, 'frozen', False)
        
        # Disable debug mode when running as exe
        debug = not is_exe
        
        if is_exe:
            # Clean up the console output for non-tech-savvy users
            # This hides the scary "WARNING: This is a development server" and HTTP request logs
            log = logging.getLogger('werkzeug')
            log.setLevel(logging.ERROR)
            
            # Remove the startup warning by overriding Werkzeug's _log
            import click
            def secho(*args, **kwargs):
                pass
            click.secho = secho
            
            # Print a friendly, clean interface
            print("\n" + "="*55)
            print(" 🚀  IMPOSTOR HUNT CTF IS RUNNING  🚀 ")
            print("="*55)
            print("\nYour web browser should open automatically in a moment.")
            print("If it doesn't, please open your browser and go to:")
            print("\n    http://127.0.0.1:5000\n")
            print("="*55)
            print(" ⚠️  DO NOT CLOSE THIS WINDOW  ⚠️")
            print(" Closing this black window will stop the game.")
            print("="*55 + "\n")

            # Open the browser unconditionally when running as exe
            threading.Timer(1.5, open_browser).start()
        else:
            if not debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
                threading.Timer(1.5, open_browser).start()
            print("Starting the Impostor Hunt server...")

        app.run(
            host  = '0.0.0.0',
            port  = port,
            debug = debug,
            use_reloader=False # Reloader must be false for .exe
        )

except Exception as e:
    print("\n" + "="*50)
    print("CRITICAL ERROR DURING STARTUP:")
    print("="*50)
    traceback.print_exc()
    print("="*50)
    input("\nPress Enter to exit...")
except SystemExit as e:
    print("\n" + "="*50)
    print(f"SYSTEM EXIT DURING STARTUP: {e}")
    print("="*50)
    traceback.print_exc()
    input("\nPress Enter to exit...")
except BaseException as e:
    print("\n" + "="*50)
    print("BASE EXCEPTION DURING STARTUP:")
    print("="*50)
    traceback.print_exc()
    print("="*50)
    input("\nPress Enter to exit...")