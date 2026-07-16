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


if __name__ == "__main__":
    executor = PythonExecutor("sample.py")

    if executor.file_exists():
        executor.show_file_info()
        executor.display_source()
    else:
        print("File not found.")