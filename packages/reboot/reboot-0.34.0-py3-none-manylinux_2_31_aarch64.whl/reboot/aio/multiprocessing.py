import multiprocessing
import threading
from multiprocessing import forkserver
from rebootdev.aio.once import Once


def _initialize_multiprocessing_start_method():
    multiprocessing_start_method = multiprocessing.get_start_method(
        allow_none=True
    )

    if multiprocessing_start_method is None:
        # We want to use 'forkserver', which should be set before any
        # threads are created, so that users _can_ use threads in
        # their tests and we will be able to reliably fork without
        # worrying about any gotchas due to forking a multi-threaded
        # process.
        multiprocessing.set_start_method('forkserver')
    elif multiprocessing_start_method != 'forkserver':
        raise RuntimeError(
            f"Reboot requires the 'forkserver' start method but you "
            f"appear to have configured '{multiprocessing_start_method}'"
        )

    # We've encountered issues when the forkserver was started while threads
    # were already running, especially if those threads were calling Objective-C
    # code, which is not allowed on macOS.
    # To avoid this, we force the forkserver to start as early as possible,
    # ensuring it runs before any other code creates threads.
    # If threads are already running when we attempt to start the forkserver,
    # and it fails, we will raise a clear error.
    try:
        forkserver.ensure_running()
    except BaseException as e:
        if threading.active_count() > 1:
            raise RuntimeError(
                f"Forkserver failed to start. {threading.active_count()} "
                "threads were already running before the attempt, "
                "which may have caused to the issue. Ensure no threads are "
                "created before initializing Reboot. Active threads:\n"
                "\n".join([thread.name for thread in threading.enumerate()])
            ) from e
        else:
            raise


# We're using a global here because we only want to initialize the
# multiprocessing start method once per process.
initialize_multiprocessing_start_method_once = Once(
    _initialize_multiprocessing_start_method
)
