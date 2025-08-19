# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from contextlib import ContextDecorator
import time
import copy


class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""


class TimerDetails:
    def __init__(self, name=None):
        self.name = name
        self.starttime = None
        self.endtime = None
        self.nest_level = None

    @property
    def duration(self):
        if self.starttime is None:
            raise TimerError("Tried to retrieve duration of a nonexistent timer")
        if self.endtime is None:
            raise TimerError("Tried to retrieve duration of an unfinished timer")

        return self.endtime - self.starttime


class Timer(ContextDecorator):
    """Time your code using a class, context manager, or decorator"""

    timers = list()
    current_nest_level = 0
    enabled = False
    precision = 6

    def __init__(self, name=None):
        self.timer_details = TimerDetails(name)

    def start(self):
        """Start a new timer"""
        if not Timer.enabled:
            return

        if self.timer_details.starttime is not None:
            if self.timer_details.endtime is not None:
                raise TimerError(
                    f"Timer for {self.timer_details.name} has already completed"
                )
            else:
                raise TimerError(
                    f"Timer for {self.timer_details.name} is running. Use .stop() to stop it"
                )

        self.timer_details.starttime = time.perf_counter()
        self.timer_details.nest_level = Timer.current_nest_level
        Timer.current_nest_level += 1

    def stop(self):
        """Stop the timer, and report the elapsed time"""
        if not Timer.enabled:
            return

        if self.timer_details.starttime is None:
            raise TimerError(
                f"Timer for {self.timer_details.name}is not running. Use .start() to start it"
            )

        if self.timer_details.endtime is not None:
            raise TimerError(
                f"Timer for {self.timer_details.name} has already completed"
            )

        self.timer_details.endtime = time.perf_counter()

        self.timers.append(copy.copy(self.timer_details))

        duration = self.timer_details.duration

        self.timer_details.starttime = None
        self.timer_details.endtime = None

        Timer.current_nest_level -= 1

        return duration

    def abort(self):
        """Abort this timer if it has been started"""
        if self.timer_details.starttime:
            self.timer_details.starttime = None
            Timer.current_nest_level -= 1

    def __enter__(self):
        """Start a new timer as a context manager"""
        self.start()
        return self

    def __exit__(self, *exc_info):
        """Stop the context manager timer"""
        self.stop()

    @staticmethod
    def setEnabled(enabled):
        Timer.enabled = enabled

    @staticmethod
    def timer_report(log_file_path):
        if not Timer.enabled or not Timer.timers:
            return

        # Summarize timings
        timer_events = list()

        for timer in Timer.timers:
            timer_events.append(
                (timer.starttime, "start", timer.name, timer.nest_level)
            )
            timer_events.append(
                (timer.endtime, timer.duration, timer.name, timer.nest_level)
            )

        start_time = timer_events[0][0]

        with open(log_file_path, "w", encoding="utf-8") as output_file:
            output_file.write("Timestamp, Task, Duration\n")
            for timestamp, duration, name, nest_level in sorted(timer_events):
                if type(duration) is not str:
                    duration = round(duration, Timer.precision)

                output_line = f'{"  " * nest_level}{(round(abs(timestamp - start_time), 2))}, {name}, {duration}\n'
                output_file.write(output_line)
