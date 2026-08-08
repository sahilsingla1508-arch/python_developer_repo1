from ast_parser import analyze
from storage import init_db, clear_events
from tracer import run_with_trace


def run_pipeline(script_path: str, db_path: str = "chronicle.db"):
    """
    Full flow: AST analyze -> reset DB -> trace script -> return static variable info.
    """
    # Static pass — what variables exist (for UI to know upfront)
    static_variables = analyze(script_path)

    # Prepare DB
    conn = init_db(db_path)
    clear_events(conn)

    # Dynamic pass — actually run + trace the script
    run_with_trace(script_path, conn)

    conn.close()
    return static_variables


if __name__ == "__main__":
    import sys
    script = sys.argv[1] if len(sys.argv) > 1 else "sample2.py"
    result = run_pipeline(script)
    print("Static variables detected:", result)
    print("Pipeline complete. Check chronicle.db for traced events.")