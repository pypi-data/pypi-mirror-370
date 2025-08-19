import os, time
from threading import Thread
from beartype import beartype
from beartype.typing import Union


class ArgoWorkflowsProgressReporter:
    def __init__(self) -> None:
        # Set the default variables
        self.current_progress = 0
        self.total_progress = 100
        self.save_interval = 2

    @beartype
    def set_current_progress(self, current_progress: Union[float, int]) -> None:
        self.current_progress = current_progress

    @beartype
    def set_total_progress(self, total_progress: Union[float, int]) -> None:
        self.total_progress = total_progress

    @beartype
    def set_progress_complete(self, default_progress: int = 100) -> None:

        if self.current_progress > self.total_progress:
            self.total_progress = self.current_progress
            return None

        if self.total_progress > self.current_progress:
            self.current_progress = self.total_progress
            return None

        if self.total_progress == self.current_progress:
            if self.total_progress == 0 or self.current_progress == 0:
                self.total_progress = default_progress
                self.current_progress = default_progress

        return None

    @beartype
    def set_save_interval(self, save_interval: Union[float, int]) -> None:
        self.save_interval = save_interval

    @beartype
    def get_progress_file_path(self) -> str:
        return os.environ.get("ARGO_PROGRESS_FILE", "/tmp/progress.txt")

    @beartype
    def get_progress_percent(self) -> Union[float, int]:
        try:
            return self.current_progress / self.total_progress
        except:
            return 0

    @beartype
    def save_file(self) -> None:
        while True:
            with open(self.get_progress_file_path(), "w") as f:
                f.write("%s/%s" % (self.current_progress, self.total_progress))
                f.close
            time.sleep(self.save_interval)

    @beartype
    def start_reporting(self) -> None:

        # Make the storage directory
        os.makedirs(os.path.dirname(self.get_progress_file_path()), exist_ok=True)

        # Start the file save thread
        t = Thread(target=self.save_file)
        t.daemon = True
        t.start()
