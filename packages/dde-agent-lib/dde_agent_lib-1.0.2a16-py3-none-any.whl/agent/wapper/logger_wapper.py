from datetime import datetime

from agent.utils.dde_logger import dde_logger as logger


def logger_wapper(fun):
    def inner(*args, **kwargs):
        logger.warning(f"{fun.__name__} begin")
        start_time = datetime.now()
        res = fun(*args, **kwargs)
        end_time = datetime.now()
        cost = (end_time - start_time).microseconds
        logger.warning(f"{fun.__name__} end, cost {cost} ms")
        return res
    return inner

