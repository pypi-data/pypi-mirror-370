import signal
import threading
import time
from collections.abc import Callable
from concurrent.futures import Future, wait, FIRST_COMPLETED

_halt_event = threading.Event()


def _handle_sigterm_or_sigint(signum, _):
    print(f"[INFO] Signal ({signum}) received. Setting halt event. Please wait...")  # Use f-string
    _halt_event.set()


signal.signal(signal.SIGINT, _handle_sigterm_or_sigint)
signal.signal(signal.SIGTERM, _handle_sigterm_or_sigint)


def halt_requested():
    return _halt_event.is_set()


def busy_loop():
    """Simulates a busy loop that can be interrupted by a signal."""
    while not _halt_event.is_set():
        time.sleep(5)


def wait_for_futures(futures: set[Future], callback: Callable[[set[Future], set[Future]], None]):
    """Waits for the completion of futures, invoking a callback with completed futures.

    This function waits indefinitely until all futures are completed or a halt signal is received.
    The callback may be invoked multiple times as futures complete, with a delay of up to 5 seconds.
    """

    completed_futures_seen = set()
    pending = set()
    while not halt_requested():
        completed, pending = wait(futures, timeout=5, return_when=FIRST_COMPLETED)
        newly_completed = completed - completed_futures_seen
        if newly_completed:
            callback(newly_completed, pending)
            completed_futures_seen.update(newly_completed)
        if not pending:
            break

    if pending and halt_requested():
        completed = futures - pending
        if completed:
            callback(completed, pending)
