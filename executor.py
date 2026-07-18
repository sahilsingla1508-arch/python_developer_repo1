import os


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
        source = self.get_source()

        print("=" * 40)
        print("Executing Program")
        print("=" * 40)

        try:
            compiled_code = compile(
                source,
                self.filename,
                "exec"
            )

            if self.tracer:
                print("Tracer enabled")

            exec(compiled_code)

            print("=" * 40)
            print("Execution Completed Successfully")
            print("=" * 40)

            return True

        except SyntaxError as error:
            print("=" * 40)
            print("Syntax Error")
            print(error)
            print("=" * 40)

            return False

        except Exception as error:
            print("=" * 40)
            print("Runtime Error")
            print(error)
            print("=" * 40)

            return False


if __name__ == "__main__":
    executor = PythonExecutor("sample.py")

    if executor.file_exists():
        executor.show_file_info()
        executor.show_source()
        executor.execute()

    else:
        print("File not found.")