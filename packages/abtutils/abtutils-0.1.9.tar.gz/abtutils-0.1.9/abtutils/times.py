import time
from typing import Union, Optional


def format_timestamp(
        timestamp: Optional[Union[float, int]] = None,
        formate: Optional[str] = None
) -> str:
    """
    将时间戳格式化为指定格式的字符串，默认使用当前时间和YYYYMMDD.HHMMSS格式

    参数:
        timestamp: 可选参数，时间戳，可为浮点数(秒级)或整数。未提供时使用当前时间
        formate: 可选参数，时间格式化字符串。未提供时使用"%Y%m%d.%H%M%S"

    返回:
        格式化后的时间字符串

    异常:
        TypeError: 当timestamp不是数字类型时触发
        ValueError: 当formate不是有效的格式化字符串时可能触发
    """
    # 如果未提供时间戳，使用当前时间戳
    if timestamp is None:
        timestamp = time.time()

    # 如果未提供格式字符串，使用默认格式
    if formate is None:
        formate = "%Y%m%d%H%M%S"

    if not isinstance(timestamp, (int, float)):
        raise TypeError("时间戳必须是整数或浮点数")

    return time.strftime(formate, time.localtime(timestamp))