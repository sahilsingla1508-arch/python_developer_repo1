import sys


def trace_calls(frame, event, arg):
    if event == "line":
        print(f"Executing line {frame.f_lineno} in {frame.f_code.co_filename}")
    return trace_calls


def run_traced(filepath: str) -> None:
    with open(filepath) as f:
        source = f.read()
    code = compile(source, filepath, "exec")

    sys.settrace(trace_calls)
    try:
        exec(code, {"__name__": "__main__"})
    finally:
        sys.settrace(None)


if __name__ == "__main__":
    # "sample_1.py" seedha likha hai kyunki ye file bhi usi (root) folder mein hai.
    run_traced("sample_1.py")