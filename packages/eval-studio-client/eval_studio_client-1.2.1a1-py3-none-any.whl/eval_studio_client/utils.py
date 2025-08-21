from typing import Optional


class ProgressBar:
    def __init__(self):
        self.progress = 0.0
        self.progress_message = "Initializing"
        self._progress_max = 1.0

    def update(self, progress: float, message: Optional[str] = None):
        try:
            self.progress = float(str(progress))
        except ValueError:
            self.progress = 0.0

        if message:
            self.progress_message = message or ""

        self.print()

    def print(self):
        print(" " * len(self.progress_message), end="\r")
        p_progress = int(self.progress / self._progress_max * 100)
        p_hashes = p_progress // 5
        p_msg = f"  {p_progress:>3}% |{'#' * p_hashes:<20}| {self.progress_message}"
        print(p_msg, end="\r")
