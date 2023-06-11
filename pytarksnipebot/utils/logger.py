import time
from functools import wraps
from queue import Queue


class Logger:
    """Handles creating and reading logs"""

    def __init__(self, queue=None, timed=True):
        """Logger init"""
        self.queue: Queue[dict[str, str | int]] = Queue() if queue is None else queue

        # time stats
        self.start_time = time.time() if timed else None
        self.time_since_start = 0

        # bot stats
        self.restarts = 0
        self.ruble_snipes = 0
        self.specific_snipes = 0
        self.snipes = 0

        # message stats
        self.message = ""

        # program stats
        self.errored = False

    def _update_queue(self):
        """updates the queue with a dictionary of mutable statistics"""
        if self.queue is None:
            return

        statistics: dict[str, str | int] = {
            "restarts": self.restarts,
            "ruble_snipes": self.ruble_snipes,
            "specific_snipes": self.specific_snipes,
            "message": self.message,
        }
        self.queue.put(statistics)

    @staticmethod
    def _updates_queue(func):
        """decorator to specify functions which update the queue with statistics"""

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            self._update_queue()  # pylint: disable=protected-access
            return result

        return wrapper

    @_updates_queue
    def add_restart(self):
        self.restarts += 1

    @_updates_queue
    def add_snipe(self):
        self.snipes += 1

    def add_ruble_snipe(self):
        self.ruble_snipes += 1
        self.snipes += 1

    def add_specific_snipe(self):
        self.specific_snipes += 1
        self.snipes += 1


    @_updates_queue
    def error(self, message: str):
        """logs an error"""
        self.errored = True
        self.status = f"Error: {message}"
        print(f"Error: {message}")

    def calc_time_since_start(self) -> str:
        if self.start_time is not None:
            hours, remainder = divmod(time.time() - self.start_time, 3600)
            minutes, seconds = divmod(remainder, 60)
        else:
            hours, minutes, seconds = 0, 0, 0
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    @_updates_queue
    def log(self, string):
        self.message = string
        self.time_since_start = self.calc_time_since_start()

        print(f"[{self.time_since_start}] {string}")

    def make_timestamp(self):
        """creates a time stamp for log output

        Returns:
            str: log time stamp
        """
        output_time = time.time() - self.start_time
        output_time = int(output_time)

        time_str = str(self.convert_int_to_time(output_time))

        output_string = time_str

        return output_string

    def convert_int_to_time(self, seconds):
        """convert epoch to time

        Args:
            seconds (int): epoch time in int

        Returns:
            str: human readable time
        """
        seconds = seconds % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        return "%d:%02d:%02d" % (hour, minutes, seconds)

