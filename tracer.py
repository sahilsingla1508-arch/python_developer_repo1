import sys

def trace_lines(frame, event, arg):
    if event == "line":
        line_no = frame.f_lineno
        local_vars = frame.f_locals.copy()
        print(f"Line {line_no}: {local_vars}")
    return trace_lines

def run_with_trace(filename):
    with open(filename, "r") as f:
        code = f.read()
    sys.settrace(trace_lines)
    exec(compile(code, filename, "exec"))
    sys.settrace(None)

if __name__ == "__main__":
    run_with_trace("sample.py")
