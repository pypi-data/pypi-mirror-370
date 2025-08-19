import asyncio
from decimal import Decimal, ROUND_HALF_UP


def retry(max_attempts=3, delay=0.5, assign_exception=Exception):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    print(f"尝试 {attempts+1} 失败: {e}")
                    await asyncio.sleep(delay)
                    attempts += 1
            raise assign_exception(f"操作失败 {max_attempts} 次")

        return wrapper

    return decorator


def round_value(value, decimal_places=0):
    """
    实现四舍五入 代替round函数 遇到5向上取整
    @param value: 传入数值
    @param decimal_places: 保留几位小数
    @return:
    """
    if isinstance(value, int):
        return value
    else:
        # 优化小数位 Decimal函数太耗时 曲线数据直接使用round函数
        # rounded_value = ("{:.%df}" % decimal_places).format(value)
        rounded_value = Decimal(str(value)).quantize(
            Decimal("1e-" + str(decimal_places)), rounding=ROUND_HALF_UP
        )
        return float(rounded_value)
