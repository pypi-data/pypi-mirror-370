import time
from datetime import timedelta

from apilinker.core.scheduler import Scheduler


def test_scheduler_interval_start_stop():
    sched = Scheduler()
    sched.add_schedule("interval", seconds=0)

    calls = {"n": 0}

    def cb():
        calls["n"] += 1
        # stop after first call
        sched.stop()

    sched.start(cb)
    # wait a bit to allow thread to run once
    time.sleep(0.1)
    assert calls["n"] >= 1

    # schedule info
    info = sched.get_schedule_info()
    assert "Every" in info or info == "No schedule configured"
