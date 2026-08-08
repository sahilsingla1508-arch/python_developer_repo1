import os
import sys
import time
from datetime import datetime

from tracer import trace_lines


class PythonExecutor:
    def __init__(self, filename, tracer=None):
        self.filename = filename
        self.tracer = tracer

    def file_exists(self):
        return os.path.exists(self.filename)

    def load_source(self):
        with open(self.filename, "r", encoding="utf-8") as file:
            return file.read()

    def get_source(self):
        return self.load_source()

    def show_source(self):
        source = self.get_source()

        print("=" * 40)
        print("Source Code")
        print("=" * 40)
        print(source)
        print("=" * 40)

    def get_file_stats(self):
        source = self.get_source()

        return {
            "filename": self.filename,
            "characters": len(source),
            "lines": len(source.splitlines())
        }

    def show_file_info(self):
        stats = self.get_file_stats()

        print("=" * 40)
        print("File Information")
        print("=" * 40)
        print("Filename   :", stats["filename"])
        print("Characters :", stats["characters"])
        print("Lines      :", stats["lines"])
        print("=" * 40)

    def execute(self):
        print("=" * 40)
        print("Executing Program")
        print("=" * 40)

        current_time = datetime.now()

        print("Execution Started :", current_time.strftime("%Y-%m-%d %H:%M:%S"))
        print("=" * 40)

        try:
            source = self.get_source()

            # ---------- Day 6 Step 2 ----------
            start_time = time.perf_counter()

            compiled_code = compile(
                source,
                self.filename,
                "exec"
            )

            if self.tracer:
                print("Tracer enabled")
                sys.settrace(self.tracer)

            execution_namespace = {}

            exec(
                compiled_code,
                execution_namespace,
                execution_namespace
            )

            # ---------- Day 6 Step 3 ----------
            end_time = time.perf_counter()
            execution_time = end_time - start_time

            print("=" * 40)
            print("Execution Completed Successfully")
            print("=" * 40)

            # ---------- Day 6 Step 4 ----------
            return {
                "success": True,
                "filename": self.filename,
                "execution_time": round(execution_time, 6),
                "error": None
            }

        except SyntaxError as error:
            print("=" * 40)
            print("Syntax Error")
            print(error)
            print("=" * 40)

            return {
                "success": False,
                "filename": self.filename,
                "error": str(error)
            }

        except Exception as error:
            print("=" * 40)
            print("Runtime Error")
            print(error)
            print("=" * 40)

            return {
                "success": False,
                "filename": self.filename,
                "error": str(error)
            }

        finally:
            if self.tracer:
                sys.settrace(None)


if __name__ == "__main__":

    target_file = "sample.py"

    executor = PythonExecutor(
        target_file,
        tracer=trace_lines
    )

    if executor.file_exists():

        executor.show_file_info()

        executor.show_source()

        result = executor.execute()

        print("=" * 40)
        print("Execution Result")
        print("=" * 40)
        print("Success        :", result["success"])
        print("Filename       :", result["filename"])
        print("Execution Time :", result.get("execution_time"), "seconds")
        print("Error          :", result["error"])
        print("=" * 40)

    else:
        print(f"File not found: {target_file}")