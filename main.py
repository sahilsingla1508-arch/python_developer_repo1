import sys
import os
from app import PyChronicleUI
from pipeline import run_pipeline

def main():
    if len(sys.argv) < 2:
        print("Usage Error: Please supply a target script.")
        print("Example: python main.py sample_2.py")
        sys.argv.append("sample_2.py")  # fixed typo: sample_2.py not sample2.py

    target_script = sys.argv[1]

    if not os.path.exists(target_script):
        print(f"File Error: '{target_script}' could not be located.")
        return

    print(f"[PyChronicle] Tracing {target_script}...")
    run_pipeline(target_script)  # populates chronicle.db before UI launches

    print(f"[PyChronicle] Launching Interactive TUI Dashboard...")
    app = PyChronicleUI(target_script=target_script)
    app.run()

if __name__ == "__main__":
    main()