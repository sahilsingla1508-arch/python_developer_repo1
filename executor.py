import os


class PythonExecutor:
    def __init__(self, filename):
        self.filename = filename

    def file_exists(self):
        return os.path.exists(self.filename)

    def load_source(self):
        with open(self.filename, "r", encoding="utf-8") as file:
            return file.read()


if __name__ == "__main__":
    executor = PythonExecutor("sample.py")

    if executor.file_exists():
        source = executor.load_source()

        print("=" * 40)
        print("Source Code Loaded Successfully")
        print("=" * 40)
        print(source)

    else:
        print("File not found.")