import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os


class Watcher:
    def __init__(self, files_to_watch):
        self.files_to_watch = {os.path.abspath(file): command for file, command in files_to_watch.items()}
        self.event_handler = Handler(self.files_to_watch)
        self.observer = Observer()

    def run(self):
        directories_to_watch = {os.path.dirname(file) for file in self.files_to_watch}
        for directory in directories_to_watch:
            self.observer.schedule(self.event_handler, directory, recursive=False)
        self.observer.start()
        print(f"Monitoring {', '.join(self.files_to_watch.keys())} for changes...")

        try:
            while True:
                time.sleep(5)  # Check every 5 seconds
        except KeyboardInterrupt:  # Ctrl + C
            self.observer.stop()
        self.observer.join()


class Handler(FileSystemEventHandler):
    def __init__(self, files_to_watch):
        super().__init__()
        self.files_to_watch = files_to_watch

    def on_modified(self, event):
        file_path = os.path.abspath(event.src_path)
        if file_path in self.files_to_watch:
            print(f"Received modified event - {file_path}")
            self.process(file_path)

    def process(self, file_path):
        command_to_run = self.files_to_watch[file_path]
        print(f"Processing file: {file_path} with command: {command_to_run}")
        # Trigger the corresponding command
        os.system(f'{command_to_run} {file_path}')


if __name__ == "__main__":

    # example command in Desktop
    # file1 = "source1.txt"
    # command1 = "python /Users/trinhlk2/Desktop/superai/watchdog/process1.py"
    # file2 = "source2.txt"
    # command2 = "python /Users/trinhlk2/Desktop/superai/watchdog/process2.py"
    # observe_command = f"python /Users/trinhlk2/Desktop/superai/watchdog/observe.py {file1}:{command1} {file2}:{command2}"
    #  python /Users/trinhlk2/Desktop/superai/watchdog/observe.py source1.txt:"python /Users/trinhlk2/Desktop/superai/watchdog/process1.py" source2.txt:"python /Users/trinhlk2/Desktop/superai/watchdog/process2.py"

    # example command in server
    # file1 = "bang_cuoc_phi.xlsx"
    # command1 = "/root/superai/crontab/run.sh --mode=init --get-data=api"
    # file2 = "phan_vung_ghep_supership.xlsx"
    # command2 = "/root/superai/crontab/run.sh --mode=init --get-data=api"
    # file3 = "ngung_giao_nhan.xlsx"
    # command3 = "/root/superai/crontab/run.sh --mode=daily --get-data=api"
    # file4 = "rst_cao_njv.xlsx"
    # command4 = "/root/superai/crontab/run.sh --mode=daily --get-data=api"
    # observe_command = f"python /root/superai/watchdog/observe.py {file1}:{command1} {file2}:{command2} {file3}:{command3} {file4}:{command4}"
    #  python /root/superai/watchdog/observe.py bang_cuoc_phi.xlsx:"/root/superai/crontab/run.sh --mode=init --get-data=api" phan_vung_ghep_supership.xlsx:"/root/superai/crontab/run.sh --mode=init --get-data=api" ngung_giao_nhan.xlsx:"/root/superai/crontab/run.sh --mode=daily --get-data=api" rst_cao_njv.xlsx:"/root/superai/crontab/run.sh --mode=daily --get-data=api"

    if len(sys.argv) < 2:
        print("Usage: python /Users/trinhlk2/Desktop/superai/watchdog/observe.py <file1>:<command1> <file2>:<command2> ...")
        # print("Usage: python /root/superai/watchdog/observe.py <file1>:<command1> <file2>:<command2> ...")
        sys.exit(1)

    files_to_commands = {}
    for arg in sys.argv[1:]:
        try:
            file, command = arg.split(':')
            files_to_commands[file] = command
        except ValueError:
            print(f"Invalid argument format: {arg}. Expected format: <file>:<command>")
            sys.exit(1)

    watcher = Watcher(files_to_commands)
    watcher.run()
