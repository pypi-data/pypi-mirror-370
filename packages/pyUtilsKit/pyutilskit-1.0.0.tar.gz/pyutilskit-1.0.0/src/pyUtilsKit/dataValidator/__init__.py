"""
dataValidator - 提供各种数据验证功能的工具库
"""

import re
from typing import Any, Optional, List, Dict, Tuple

def isEmail(emailStr: str) -> bool:
    """
    验证字符串是否为有效的电子邮件格式
    
    Args:
        emailStr: 待验证的电子邮件字符串
        
    Returns:
        如果是有效电子邮件格式返回True，否则返回False
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, emailStr) is not None

def isPhoneNumber(
    phoneStr: str,
    countryCode: Optional[str] = 'CN'
) -> bool:
    """
    验证字符串是否为有效的电话号码格式
    
    Args:
        phoneStr: 待验证的电话号码字符串
        countryCode: 国家代码，支持CN/US/UK
        
    Returns:
        如果是有效电话号码格式返回True，否则返回False
    """
    patterns = {
        'CN': r'^1[3-9]\d{9}$',
        'US': r'^\+1\d{10}$',
        'UK': r'^\+44\d{10}$'
    }
    pattern = patterns.get(countryCode, patterns['CN'])
    return re.match(pattern, phoneStr) is not None

def isInRange(
    value: int,
    minVal: int,
    maxVal: int
) -> bool:
    """
    验证数值是否在指定范围内
    
    Args:
        value: 待验证的数值
        minVal: 最小值(包含)
        maxVal: 最大值(包含)
        
    Returns:
        如果在范围内返回True，否则返回False
        
    Raises:
        ValueError: 如果最小值大于最大值
    """
    if minVal > maxVal:
        raise ValueError("最小值不能大于最大值")
    return minVal <= value <= maxVal

def isListValid(
    inputList: List[Any],
    minLength: int = 0,
    maxLength: Optional[int] = None
) -> bool:
    """
    验证列表是否满足长度要求
    
    Args:
        inputList: 待验证的列表
        minLength: 最小长度要求
        maxLength: 最大长度要求(可选)
        
    Returns:
        如果满足长度要求返回True，否则返回False
        
    Raises:
        ValueError: 如果最小长度为负数
    """
    if minLength < 0:
        raise ValueError("最小长度不能为负数")
    length = len(inputList)
    if maxLength is not None:
        return minLength <= length <= maxLength
    return length >= minLength

def isDictValid(
    inputDict: Dict[Any, Any],
    requiredKeys: Optional[List[Any]] = None
) -> bool:
    """
    验证字典是否包含所有必需的键
    
    Args:
        inputDict: 待验证的字典
        requiredKeys: 必须包含的键列表
        
    Returns:
        如果包含所有必需键返回True，否则返回False
    """
    if requiredKeys is None:
        return True
    return all(key in inputDict for key in requiredKeys)

def validateWithRegex(
    inputStr: str,
    pattern: str,
    flags: int = 0
) -> bool:
    """
    使用正则表达式验证字符串
    
    Args:
        inputStr: 待验证的字符串
        pattern: 正则表达式模式
        flags: 正则表达式标志
        
    Returns:
        如果匹配成功返回True，否则返回False
        
    Raises:
        re.error: 如果正则表达式模式无效
    """
    return re.match(pattern, inputStr, flags) is not None

def isDateValid(
    dateStr: str,
    format: str = '%Y-%m-%d'
) -> bool:
    """
    验证日期字符串是否符合指定格式
    
    Args:
        dateStr: 待验证的日期字符串
        format: 日期格式字符串
        
    Returns:
        如果是有效日期返回True，否则返回False
    """
    try:
        from datetime import datetime
        datetime.strptime(dateStr, format)
        return True
    except ValueError:
        return False

def isAllSameType(items: List[Any]) -> bool:
    """
    验证列表中所有元素是否为相同类型
    
    Args:
        items: 待验证的列表
        
    Returns:
        如果所有元素类型相同返回True，否则返回False
    """
    if not items:
        return True
    firstType = type(items[0])
    return all(isinstance(item, firstType) for item in items[1:])

def isJsonString(jsonStr: str) -> bool:
    """
    验证字符串是否为有效的JSON格式
    
    Args:
        jsonStr: 待验证的JSON字符串
        
    Returns:
        如果是有效JSON返回True，否则返回False
    """
    try:
        import json
        json.loads(jsonStr)
        return True
    except ValueError:
        return False