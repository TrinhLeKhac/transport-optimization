import os
import sys
from datetime import datetime


def process_file(file_path):
    print(f"Processing file: {file_path}")
    # Implement your file processing logic here
    with open(file_path, 'r') as file:
        content = file.read()
        print(content)


def main(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    # Get the last modified time
    last_modified_time = os.path.getmtime(file_path)
    last_modified_time = datetime.fromtimestamp(last_modified_time)
    print(f"Last modified time: {last_modified_time}")

    process_file(file_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python /Users/trinhlk2/Desktop/superai/watchdog/process1.py <file_path(relative)>")
        sys.exit(1)

    file_path = sys.argv[1]
    main(file_path)
