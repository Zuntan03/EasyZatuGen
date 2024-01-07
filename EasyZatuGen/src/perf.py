import time


class Perf:
    ctx = None

    @classmethod
    def start(cls):
        return time.perf_counter()

    @classmethod
    def end(cls, start_time, name=None, info=None):
        if (not cls.ctx is None) and (not cls.ctx.cfg.easy_zatu_gen["enable_perf_log"]):
            return
        msg = "["
        if name is not None:
            msg += f"{name}: "
        msg += f"{time.perf_counter() - start_time:.1f}sec]"
        if info is not None:
            msg += f" ({info})"
        print(msg)
