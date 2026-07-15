import os


class PythonExecutor:
    def __init__(self, filename):
        self.filename = filename


if __name__ == "__main__":
    executor = PythonExecutor("sample.py")
    print("Executor object created successfully")