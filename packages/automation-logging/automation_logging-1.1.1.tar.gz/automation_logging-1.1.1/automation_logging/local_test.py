from protocols import IAutomationLogger


from profiler import Profiler
import global_logger as log
import core

if __name__ == "__main__":
    import time

    core.AutomationLogger("test", "local_logs")

    @Profiler("ms")
    def foo():
        time.sleep(0.1)

    t1 = time.monotonic()
    for _ in range(2):
        foo()
    t2 = time.monotonic()
    print(t2 - t1)
    print(foo.__getattribute__("profiler"))

    logger: IAutomationLogger | None = log.get_global_log()
    assert isinstance(logger, core.AutomationLogger), "error"
    pass
