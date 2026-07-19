import sys

from ui.app import PyChronicleApp


def main():

    if len(sys.argv) != 2:

        print("Usage:")

        print("python main.py <python_file>")

        return

    filename = sys.argv[1]

    app = PyChronicleApp(filename)

    app.run()


if __name__ == "__main__":
    main()
