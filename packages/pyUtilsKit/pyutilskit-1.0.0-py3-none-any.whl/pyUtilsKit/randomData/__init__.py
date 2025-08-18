"""
randomData - 一个用于生成各种随机数据的Python函数库，包括随机字符串、数字、日期、颜色等。
"""

import random
import string
from datetime import datetime, timedelta
from typing import Union, List, Tuple, Optional


def genRandomStr(
    length: int = 8,
    includeDigits: bool = True,
    includeSpecial: bool = False
) -> str:
    """
    生成随机字符串
    
    Args:
        length: 字符串长度，默认为8
        includeDigits: 是否包含数字，默认为True
        includeSpecial: 是否包含特殊字符，默认为False
        
    Returns:
        str: 生成的随机字符串
        
    Raises:
        ValueError: 如果length小于等于0
    """
    if length <= 0:
        raise ValueError("长度必须大于0")
        
    chars = string.ascii_letters
    if includeDigits:
        chars += string.digits
    if includeSpecial:
        chars += string.punctuation
        
    return ''.join(random.choice(chars) for _ in range(length))


def genRandomInt(minVal: int = 0, maxVal: int = 100) -> int:
    """
    生成随机整数
    
    Args:
        minVal: 最小值，默认为0
        maxVal: 最大值，默认为100
        
    Returns:
        int: 生成的随机整数
        
    Raises:
        ValueError: 如果minVal大于maxVal
    """
    if minVal > maxVal:
        raise ValueError("最小值不能大于最大值")
        
    return random.randint(minVal, maxVal)


def genRandomFloat(
    minVal: float = 0.0,
    maxVal: float = 1.0, 
    decimalPlaces: int = 2
) -> float:
    """
    生成随机浮点数
    
    Args:
        minVal: 最小值，默认为0.0
        maxVal: 最大值，默认为1.0
        decimalPlaces: 小数位数，默认为2
        
    Returns:
        float: 生成的随机浮点数
        
    Raises:
        ValueError: 如果minVal大于maxVal或decimalPlaces小于0
    """
    if minVal > maxVal:
        raise ValueError("最小值不能大于最大值")
    if decimalPlaces < 0:
        raise ValueError("小数位数不能为负数")
        
    randFloat = random.uniform(minVal, maxVal)
    return round(randFloat, decimalPlaces)


def genRandomDate(
    startDate: str = "2000-01-01", 
    endDate: str = "2023-12-31",
    dateFormat: Optional[str] = None
) -> str:
    """
    生成随机日期
    
    Args:
        startDate: 开始日期，格式为YYYY-MM-DD，默认为"2000-01-01"
        endDate: 结束日期，格式为YYYY-MM-DD，默认为"2023-12-31"
        dateFormat: 返回日期的格式，None表示使用YYYY-MM-DD格式 (%Y-%m-%d)
        
    Returns:
        str: 生成的随机日期
        
    Raises:
        ValueError: 如果日期格式无效或startDate晚于endDate
    """
    try:
        start = datetime.strptime(startDate, "%Y-%m-%d")
        end = datetime.strptime(endDate, "%Y-%m-%d")
    except ValueError:
        raise ValueError("日期格式应为YYYY-MM-DD")
        
    if start > end:
        raise ValueError("开始日期不能晚于结束日期")
        
    delta = end - start
    randomDays = random.randint(0, delta.days)
    randomDate = start + timedelta(days=randomDays)
    
    return randomDate.strftime(dateFormat if dateFormat else "%Y-%m-%d")


def genRandomColor(colorFormat: str = "hex") -> Union[str, Tuple[int, int, int]]:
    """
    生成随机颜色
    
    Args:
        colorFormat: 颜色格式，可选"hex"或"rgb"，默认为"hex"
        
    Returns:
        Union[str, Tuple[int, int, int]]: 十六进制颜色字符串或RGB元组
        
    Raises:
        ValueError: 如果colorFormat不是"hex"或"rgb"
    """
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    
    if colorFormat == "hex":
        return "#{:02x}{:02x}{:02x}".format(r, g, b)
    elif colorFormat == "rgb":
        return (r, g, b)
    else:
        raise ValueError("颜色格式必须是'hex'或'rgb'")


def genRandomFromList(items: List, num: int = 1, 
                     allowDuplicates: bool = False) -> Union[object, List[object]]:
    """
    从列表中随机选择元素
    
    Args:
        items: 源列表
        num: 要选择的元素数量，默认为1
        allowDuplicates: 是否允许重复选择，默认为False
        
    Returns:
        Union[object, List[object]]: 当num=1时返回单个元素，否则返回列表
        
    Raises:
        ValueError: 如果items为空，或num无效，或不允许重复时num大于列表长度
    """
    if not items:
        raise ValueError("源列表不能为空")
    if num <= 0:
        raise ValueError("数量必须大于0")
    if not allowDuplicates and num > len(items):
        raise ValueError("不允许重复时，数量不能大于列表长度")
        
    if allowDuplicates:
        selected = [random.choice(items) for _ in range(num)]
    else:
        selected = random.sample(items, num)
        
    return selected[0] if num == 1 else selected


def genRandomBool(trueProb: float = 0.5) -> bool:
    """
    生成随机布尔值
    
    Args:
        trueProb: 返回True的概率，默认为0.5
        
    Returns:
        bool: 随机布尔值
        
    Raises:
        ValueError: 如果trueProb不在0到1之间
    """
    if not 0 <= trueProb <= 1:
        raise ValueError("概率必须在0到1之间")
        
    return random.random() < trueProb


def genRandomName(nameType: str = "first") -> str:
    """
    生成随机名字
    
    Args:
        nameType: 名字类型，"first"表示姓，"last"表示名，默认为"first"
        
    Returns:
        str: 随机生成的名字
        
    Raises:
        ValueError: 如果nameType不是"first"或"last"
    """
    firstNames = ["张", "王", "李", "赵", "刘", "陈", "杨", "黄", "周", "吴"]
    lastNames = ["伟", "芳", "娜", "秀英", "敏", "静", "丽", "强", "磊", "军"]
    
    if nameType == "first":
        return random.choice(firstNames)
    elif nameType == "last":
        return random.choice(lastNames)
    else:
        raise ValueError("名字类型必须是'first'或'last'")