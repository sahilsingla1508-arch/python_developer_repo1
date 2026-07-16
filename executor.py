import os


class PythonExecutor:
    def __init__(self, filename):
        self.filename = filename

    def file_exists(self):
        return os.path.exists(self.filename)

    def load_source(self):
        with open(self.filename, "r", encoding="utf-8") as file:
            return file.read()

    def get_source(self):
        return self.load_source()

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

    def display_source(self):
        print("=" * 40)
        print("Source Code")
        print("=" * 40)
        print(self.get_source())
        print("=" * 40)

    def execute(self):
        if not self.file_exists():
            raise FileNotFoundError(f"{self.filename} not found.")

        source = self.get_source()

        compiled_code = compile(source, self.filename, "exec")

        print("=" * 40)
        print("Executing Program")
        print("=" * 40)

        exec(compiled_code)

        print("=" * 40)
        print("Execution Completed Successfully")
        print("=" * 40)

        return True


if __name__ == "__main__":
    executor = PythonExecutor("sample.py")

    try:
        executor.show_file_info()
        executor.display_source()
        executor.execute()

    except FileNotFoundError as e:
        print(e)

    except Exception as e:
        print("Execution Error:", e)