"""
mathUtils - 提供各种数学计算功能的工具库

功能包括：
- 基本数学运算
- 统计计算
- 几何计算
- 数值分析
- 随机数生成
"""

import math
import random
from typing import List, Tuple, Optional, Union

def clamp(
    value: Union[int, float],
    minVal: Union[int, float],
    maxVal: Union[int, float]
) -> Union[int, float]:
    """
    将值限制在指定范围内
    
    Args:
        value: 要限制的值
        minVal: 最小值
        maxVal: 最大值
        
    Returns:
        限制后的值
        
    Raises:
        ValueError: 如果最小值大于最大值
    """
    if minVal > maxVal:
        raise ValueError("最小值不能大于最大值")
    return max(minVal, min(value, maxVal))

def lerp(
    a: Union[int, float],
    b: Union[int, float],
    t: float
) -> float:
    """
    线性插值计算
    
    Args:
        a: 起始值
        b: 结束值
        t: 插值因子(0-1之间)
        
    Returns:
        插值结果
        
    Raises:
        ValueError: 如果t不在0-1范围内
    """
    if t < 0 or t > 1:
        raise ValueError("插值因子必须在0和1之间")
    return a + (b - a) * t

def calculateDistance(
    x1: float,
    y1: float,
    x2: float,
    y2: float
) -> float:
    """
    计算两点之间的欧几里得距离
    
    Args:
        x1: 第一个点的x坐标
        y1: 第一个点的y坐标
        x2: 第二个点的x坐标
        y2: 第二个点的y坐标
        
    Returns:
        两点之间的距离
    """
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def calculateAverage(numbers: List[float]) -> float:
    """
    计算数字列表的平均值
    
    Args:
        numbers: 数字列表
        
    Returns:
        平均值
        
    Raises:
        ValueError: 如果列表为空
    """
    if not numbers:
        raise ValueError("数字列表不能为空")
    return sum(numbers) / len(numbers)

def calculateStandardDeviation(
    numbers: List[float],
    isSample: bool = False
) -> float:
    """
    计算数字列表的标准差
    
    Args:
        numbers: 数字列表
        isSample: 是否为样本数据
        
    Returns:
        标准差
        
    Raises:
        ValueError: 如果列表为空或样本数据但只有一个元素
    """
    if not numbers:
        raise ValueError("数字列表不能为空")
    if isSample and len(numbers) == 1:
        raise ValueError("样本数据需要至少两个元素")
    
    avg = calculateAverage(numbers)
    variance = sum((x - avg) ** 2 for x in numbers) / (len(numbers) - (1 if isSample else 0))
    return math.sqrt(variance)

def generateRandomInt(
    minVal: int,
    maxVal: int,
    exclude: Optional[List[int]] = None
) -> int:
    """
    生成指定范围内的随机整数
    
    Args:
        minVal: 最小值(包含)
        maxVal: 最大值(包含)
        exclude: 要排除的值列表
        
    Returns:
        随机整数
        
    Raises:
        ValueError: 如果范围无效或所有值都被排除
    """
    if minVal > maxVal:
        raise ValueError("最小值不能大于最大值")
    
    exclude = exclude or []
    available = [x for x in range(minVal, maxVal + 1) if x not in exclude]
    
    if not available:
        raise ValueError("没有可用的随机数")
    return random.choice(available)

def isPrime(number: int) -> bool:
    """
    检查数字是否为质数
    
    Args:
        number: 要检查的数字
        
    Returns:
        如果是质数返回True，否则返回False
        
    Raises:
        ValueError: 如果数字小于2
    """
    if number < 2:
        raise ValueError("数字必须大于等于2")
    if number % 2 == 0:
        return number == 2
    for i in range(3, int(math.sqrt(number)) + 1, 2):
        if number % i == 0:
            return False
    return True

def calculateCircleArea(radius: float) -> float:
    """
    计算圆的面积
    
    Args:
        radius: 圆的半径
        
    Returns:
        圆的面积
        
    Raises:
        ValueError: 如果半径为负数
    """
    if radius < 0:
        raise ValueError("半径不能为负数")
    return math.pi * radius ** 2

def normalizeAngle(angle: float) -> float:
    """
    将角度标准化到0-360度范围内
    
    Args:
        angle: 输入角度
        
    Returns:
        标准化后的角度
    """
    return angle % 360

def calculateFactorial(n: int) -> int:
    """
    计算阶乘
    
    Args:
        n: 要计算阶乘的数字
        
    Returns:
        阶乘结果
        
    Raises:
        ValueError: 如果n为负数
    """
    if n < 0:
        raise ValueError("不能计算负数的阶乘")
    return 1 if n == 0 else n * calculateFactorial(n - 1)

def solveQuadraticEquation(
    a: float,
    b: float,
    c: float
) -> Tuple[Optional[float], Optional[float]]:
    """
    解二次方程 ax² + bx + c = 0
    
    Args:
        a: 二次项系数
        b: 一次项系数
        c: 常数项
        
    Returns:
        包含两个解的元组(可能为None)
    """
    discriminant = b**2 - 4*a*c
    if discriminant < 0:
        return (None, None)
    sqrtDiscriminant = math.sqrt(discriminant)
    x1 = (-b + sqrtDiscriminant) / (2*a)
    x2 = (-b - sqrtDiscriminant) / (2*a)
    return (x1, x2)