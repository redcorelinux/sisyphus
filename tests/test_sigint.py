import importlib
import os
import signal
import subprocess
import threading
import time

import animation
import pytest

import sisyphus.syncenv

# Modules that install a module-level SIGINT handler and rely on
# "except KeyboardInterrupt" to stop the emerge/git child process cleanly.
MODULES = [
    "depsolve",
    "pkgadd",
    "pkgremove",
    "revdepsolve",
    "searchdb",
    "setbranch",
    "setprofile",
    "syncall",
    "syncenv",
    "sysclean",
    "sysupgrade",
]


def send_sigint_after(delay):
    timer = threading.Timer(delay, os.kill, (os.getpid(), signal.SIGINT))
    timer.start()
    return timer


@pytest.mark.parametrize("name", MODULES)
def test_handler_raises_keyboard_interrupt(name):
    # Bug 144: the handlers used to call sys.exit(0), so the
    # "except KeyboardInterrupt" clean-up blocks never ran.
    module = importlib.import_module(f"sisyphus.{name}")
    with pytest.raises(KeyboardInterrupt):
        module.sigint_handler(signal.SIGINT, None)


def test_ctrl_c_is_not_swallowed_by_the_animation_library():
    # Bug 130: the animation library installs a SIGINT handler that only stops
    # its spinners and returns, so Ctrl+C did nothing. Sisyphus must still
    # override it.
    assert signal.getsignal(signal.SIGINT) is not getattr(
        animation.decorators, "end_wait_threads", None)

    with pytest.raises(KeyboardInterrupt):
        os.kill(os.getpid(), signal.SIGINT)
        time.sleep(1)


def test_ctrl_c_stops_a_spinner_function():
    # Bug 130 again: Ctrl+C inside an @animation.wait function must stop
    # both the function and the spinner thread.
    before = threading.active_count()

    @animation.wait('testing')
    def long_job():
        time.sleep(5)

    timer = send_sigint_after(0.3)
    started = time.monotonic()
    with pytest.raises(KeyboardInterrupt):
        long_job()
    timer.join()

    assert time.monotonic() - started < 2
    time.sleep(0.5)  # give the spinner thread time to notice it was stopped
    assert threading.active_count() == before


def test_ctrl_c_stops_the_child_before_sisyphus_exits(monkeypatch):
    # Bug 144: Sisyphus must stop its child process (emerge, git) before it
    # exits, so no child output appears after the shell prompt.
    children = []
    real_popen = subprocess.Popen

    def recording_popen(*args, **kwargs):
        proc = real_popen(*args, **kwargs)
        children.append(proc)
        return proc

    monkeypatch.setattr(subprocess, "Popen", recording_popen)

    timer = send_sigint_after(0.3)
    try:
        with pytest.raises(SystemExit):
            sisyphus.syncenv.run_git(["sleep", "30"])
        # Checked before the clean-up below, which would stop it anyway.
        child_status = children[0].poll()
    finally:
        timer.join()
        for proc in children:
            if proc.poll() is None:
                proc.kill()
                proc.wait()

    assert len(children) == 1
    # The clean-up code ran: the child had already stopped when run_git exited.
    assert child_status is not None
    assert child_status != 0
