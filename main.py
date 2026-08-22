import sys
import os

from app import PyChronicleUI
from pipeline import run_pipeline
from launch_screen import LaunchApp


def main():
    if len(sys.argv) < 2:
        # No script supplied — show the interactive launch/selection screen
        launch = LaunchApp()
        launch.run()

        target_script = launch.selected_script
        if not target_script:
            # User pressed Esc or closed without confirming
            print("[PyChronicle] No script selected. Exiting.")
            return
    else:
        target_script = sys.argv[1]

    if not os.path.exists(target_script):
        print(f"[PyChronicle] File Error: '{target_script}' could not be located.")
        return

    print(f"[PyChronicle] Tracing {target_script}...")
    run_pipeline(target_script)  # populates chronicle.db before UI launches

    print(f"[PyChronicle] Launching Interactive TUI Dashboard...")
    app = PyChronicleUI(target_script=target_script)
    app.run()


if __name__ == "__main__":
    main()