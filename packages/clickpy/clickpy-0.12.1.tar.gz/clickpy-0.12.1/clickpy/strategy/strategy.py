"""Click Strategy implementation using __init__subclass pattern."""

from abc import ABC, abstractmethod
from random import randint
from time import sleep
from typing import Callable

import pyautogui
import typer

_STDOUT = typer.echo


class ClickStrategy(ABC):
    @abstractmethod
    def click(self) -> None: ...  # pragma: no cover


class BasicClickStrategy(ClickStrategy):
    """The first, very basic clicking strategy I came up with.

    Before clicking, __click__ will tell the current thread to sleep.
    If self.sleep_time has a value, it will use that as the thread sleep time.
    Else, it will generate a random number between 1 and 180 (3 minutes).
    """

    min_time = 1
    max_time = 180
    debug_msg = "Thread sleeping for {0} seconds."

    def __init__(
        self,
        *,
        debug: bool = False,
        fast: bool = False,
        stdout: Callable | None = None,
        **kwargs,
    ):
        """Init fields."""
        if stdout is None:
            self._stdout = _STDOUT
        self.debug = debug
        self.fast = fast

        if self.fast:
            self._timer = 0.5

    def click(self) -> None:
        """
        Protocol method defined by SupportsClick.

        Process:
        1. Either use the sleep_time passed into the ctr, or get a random int
        between min_sleep_time and max_sleep_time.
        2. Pause the current thread with above int (in seconds).
        3. call pyautogui.click()
        Optional: print statements if print_debug = True.
        """
        if not self.fast:
            self._timer = float(randint(self.min_time, self.max_time))

        if self.debug:
            self._stdout(self.debug_msg.format(self._timer))

        sleep(self._timer)
        pyautogui.click()

        if self.debug:
            self._stdout("! Clicked !")


class NaturalClickStrategy(ClickStrategy):
    """Click Strategy to replicate a more natural clicking pattern."""

    min_time = 2
    max_time = 60
    debug_msg = "Thread sleeping for {0} seconds."
    timers = [1.0, 1.0, 2.5]

    def __init__(
        self, *, debug: bool = False, stdout: Callable | None = None, **kwargs
    ):
        """Init fields."""
        if stdout is None:
            self._stdout = _STDOUT
        self.debug = debug

    def click(self):
        """Protocol method defined by SupportsClick.

        Process:
        Define a list of 'wait times', i.e. time in between clicks.
        In a loop, click mouse then sleep that iterations wait time.
        At the end, get a random time between min and max bounds.
        """
        timers = self.timers + [float(randint(self.min_time, self.max_time))]
        if self.debug:
            self._stdout(f"Natural click timers: {timers}.\n")

        for time in timers:
            if self.debug:
                self._stdout(self.debug_msg.format(time))

            sleep(time)
            pyautogui.click()

            if self.debug:
                self._stdout("! Clicked !")
