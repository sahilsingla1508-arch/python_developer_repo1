import sys
import os
from ui.app import PyChronicleUI  # Adjust import if app.py is in the root

def main():
    """CLI Execution Runner."""
    if len(sys.argv) < 2:
        print("[PyChronicle] Error: Missing script argument.")
        print("Usage: python main.py <target_script.py>")
        sys.argv.append("sample_1.py") # Fallback script

    target_script = sys.argv[1]
    db_path = "chronicle.db"

    if not os.path.exists(target_script):
        print(f"[PyChronicle] Error: Target file '{target_script}' not found.")
        return

    print(f"[PyChronicle] Launching TUI Time-Travel Debugger for: {target_script}")
    app = PyChronicleUI(target_script=target_script, db_path=db_path)
    app.run()

if __name__ == "__main__":
    main()
