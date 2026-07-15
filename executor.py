import os


class PythonExecutor:
    def __init__(self, filename):
        self.filename = filename

    def file_exists(self):
        return os.path.exists(self.filename)

    def load_source(self):
        with open(self.filename, "r", encoding="utf-8") as file:
            return file.read()

    def show_file_info(self):
        source = self.load_source()

        print("=" * 40)
        print("File Information")
        print("=" * 40)
        print("Filename :", self.filename)
        print("Characters :", len(source))
        print("Lines :", len(source.splitlines()))
        print("=" * 40)


if __name__ == "__main__":
    executor = PythonExecutor("sample.py")

    if executor.file_exists():
        executor.show_file_info()

    else:
        print("File not found.")