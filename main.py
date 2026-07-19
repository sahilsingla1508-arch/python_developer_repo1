import sys
import os
from app import PyChronicleUI

def main():
    # Enforces CLI syntax configuration: python main.py <target_script.py>
    if len(sys.argv) < 2:
        print("Usage Error: Please supply a target script.")
        print("Example: python main.py sample.py")
        sys.argv.append("sample2.py") # Fallback to prevent crash if run via IDE play button

    target_script = sys.argv[1]
    
    if not os.path.exists(target_script):
        print(f"File Error: '{target_script}' could not be located.")
        return

    print(f"[PyChronicle] Launching Interactive TUI Dashboard tracking: {target_script}...")
    app = PyChronicleUI(target_script=target_script)
    app.run()

if __name__ == "__main__":
    main()
