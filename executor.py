import os


class PythonExecutor:
    def __init__(self, filename):
        self.filename = filename

    def file_exists(self):
        return os.path.exists(self.filename)


if __name__ == "__main__":
    executor = PythonExecutor("sample.py")

    if executor.file_exists():
        print("File exists")
    else:
        print("File not found")