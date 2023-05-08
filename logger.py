import time


class Logger:
    """Handles creating and reading logs"""

    def __init__(self):
        """Logger init"""
        self.start_time = time.time()
        self.restarts = 0
        self.snipes = 0

        self.current_status = ""

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

    def change_status(self, status):
        self.current_status = status
        self.print_new_terminal()

    def add_restart(self):
        """add restart to log"""
        self.restarts += 1
        self.print_new_terminal()

    def add_snipe(self):
        self.snipes = self.snipes + 1
        self.print_new_terminal()

    def print_new_terminal(self):
        print(self.current_status)
