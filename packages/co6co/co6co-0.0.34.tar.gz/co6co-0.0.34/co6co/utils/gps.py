
from fractions import Fraction


def dms_to_decimal(degrees: float, minutes: float, seconds: float, direction: str = None):
    """
    将度、分、秒格式的坐标转换为十进制分数格式。

    :param degrees: 度数 (float)
    :param minutes: 分数 (float)
    :param seconds: 秒数 (float)
    :param direction: 方向 ('N', 'S', 'E', 'W')，可选参数
    :return:  分数形式可以防止精度丢失，十进制分数格式的坐标 float(1/100) 将分数转小数
    """
    degrees_fraction = Fraction(degrees)
    minutes_fraction = Fraction(minutes, 60)
    seconds_fraction = Fraction(seconds, 3600)

    decimal_value = degrees_fraction + minutes_fraction + seconds_fraction
    # 根据方向调整正负号
    if direction in ['S', 'W']:
        decimal_value = -decimal_value

    return decimal_value
