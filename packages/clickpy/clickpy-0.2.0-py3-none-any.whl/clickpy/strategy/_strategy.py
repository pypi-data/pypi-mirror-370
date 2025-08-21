"""Click Strategy implementation using __init__subclass pattern."""
from abc import ABC, abstractmethod
from random import randint
from time import sleep

import pyautogui
import typer


class ClickStrategy(ABC):
    @abstractmethod
    def click(self) -> None:
        pass


class BasicClickStrategy(ClickStrategy):  # this line will trigger __init_subclass__
    """The first, very basic clicking strategy I came up with.

    Before clicking, __click__ will tell the current thread to sleep.
    If self.sleep_time has a value, it will use that as the thread sleep time.
    Else, it will generate a random number between 1 and 180 (3 minutes).
    """

    def __init__(self, **kwargs):
        """Init fields."""
        self.debug = kwargs.pop("debug", False)
        self.fast = kwargs.pop("fast", False)
        self.min_bound: int = 1
        self.max_bound: int = 180

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
        timer = 0.5 if self.fast else float(randint(self.min_bound, self.max_bound))

        if self.debug and not self.fast:
            typer.echo(f"Random thread sleep for {timer} seconds.")

        if self.debug:
            typer.echo("Thread sleeping now...")

        sleep(timer)
        pyautogui.click()

        if self.debug:
            typer.echo("... Clicked")


class NaturalClickStrategy(ClickStrategy):
    """Click Strategy to replicate a more natural clicking pattern."""

    def __init__(self, **kwargs):
        """Init fields."""
        self.debug = kwargs.pop("debug", False)
        self.min_bound = 5
        self.max_bound = 60
        self.wait_times = [1.0, 1.0, 2.5, randint(self.min_bound, self.max_bound)]

    def click(self):
        """Protocol method defined by SupportsClick.

        Process:
        Define a list of 'wait times', i.e. time in between clicks.
        In a loop, click mouse then sleep that iterations wait time.
        At the end, get a random time between min and max bounds.
        """
        for time in self.wait_times:
            if self.debug:
                typer.echo(f"Waiting for {time} sec ...")

            sleep(time)
            pyautogui.click()

            if self.debug:
                typer.echo("... Clicked")
