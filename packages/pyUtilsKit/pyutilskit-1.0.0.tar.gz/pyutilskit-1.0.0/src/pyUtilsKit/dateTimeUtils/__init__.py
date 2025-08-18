"""
dateTimeUtils - 提供日期时间处理功能的工具库
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
import pytz
import calendar

def formatDateTime(
    dt: datetime,
    formatStr: str = "%Y-%m-%d %H:%M:%S"
) -> str:
    """
    格式化日期时间对象为字符串
    
    Args:
        dt: 要格式化的datetime对象
        formatStr: 格式字符串
        
    Returns:
        格式化后的日期时间字符串
    """
    return dt.strftime(formatStr)

def parseDateTime(
    dateStr: str,
    formatStr: str = "%Y-%m-%d %H:%M:%S"
) -> datetime:
    """
    从字符串解析日期时间
    
    Args:
        dateStr: 日期时间字符串
        formatStr: 格式字符串
        
    Returns:
        解析后的datetime对象
        
    Raises:
        ValueError: 如果字符串与格式不匹配
    """
    return datetime.strptime(dateStr, formatStr)

def addDays(
    dt: datetime,
    days: int
) -> datetime:
    """
    添加指定天数到日期时间
    
    Args:
        dt: 原始日期时间
        days: 要添加的天数(可为负)
        
    Returns:
        计算后的新日期时间
    """
    return dt + timedelta(days=days)

def getWeekday(
    dt: datetime,
    abbreviate: bool = False
) -> str:
    """
    获取星期几
    
    Args:
        dt: 日期时间对象
        abbreviate: 是否返回缩写
        
    Returns:
        星期几的名称或缩写
    """
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    abbrs = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    weekday = dt.weekday()
    return abbrs[weekday] if abbreviate else weekdays[weekday]

def isWeekend(dt: datetime) -> bool:
    """
    检查日期是否是周末
    
    Args:
        dt: 要检查的日期时间
        
    Returns:
        如果是周末返回True，否则返回False
    """
    return dt.weekday() >= 5

def convertTimezone(
    dt: datetime,
    fromTz: str,
    toTz: str
) -> datetime:
    """
    转换时区
    
    Args:
        dt: 要转换的日期时间(无时区信息)
        fromTz: 原始时区
        toTz: 目标时区
        
    Returns:
        转换时区后的新日期时间
        
    Raises:
        pytz.exceptions.UnknownTimeZoneError: 如果时区无效
    """
    fromZone = pytz.timezone(fromTz)
    toZone = pytz.timezone(toTz)
    localized = fromZone.localize(dt)
    return localized.astimezone(toZone)

def getLastDayOfMonth(
    year: int,
    month: int
) -> int:
    """
    获取某月的最后一天
    
    Args:
        year: 年份
        month: 月份
        
    Returns:
        该月的最后一天
    """
    return calendar.monthrange(year, month)[1]

def dateDiff(
    dt1: datetime,
    dt2: datetime,
    unit: str = "days"
) -> int:
    """
    计算两个日期时间的差值
    
    Args:
        dt1: 第一个日期时间
        dt2: 第二个日期时间
        unit: 单位(days/seconds/minutes/hours)
        
    Returns:
        时间差数值
        
    Raises:
        ValueError: 如果单位无效
    """
    delta = dt1 - dt2
    if unit == "days":
        return abs(delta.days)
    elif unit == "seconds":
        return abs(int(delta.total_seconds()))
    elif unit == "minutes":
        return abs(int(delta.total_seconds() / 60))
    elif unit == "hours":
        return abs(int(delta.total_seconds() / 3600))
    else:
        raise ValueError("无效的单位")

def isLeapYear(year: int) -> bool:
    """
    检查是否是闰年
    
    Args:
        year: 要检查的年份
        
    Returns:
        如果是闰年返回True，否则返回False
    """
    return calendar.isleap(year)

def getCurrentDateTime(timezone: Optional[str] = None) -> datetime:
    """
    获取当前日期时间
    
    Args:
        timezone: 时区名称(可选)
        
    Returns:
        当前日期时间(有时区信息)
    """
    if timezone:
        tz = pytz.timezone(timezone)
        return datetime.now(tz)
    return datetime.now()

def isValidDate(
    year: int,
    month: int,
    day: int
) -> bool:
    """
    验证日期是否有效
    
    Args:
        year: 年
        month: 月
        day: 日
        
    Returns:
        如果日期有效返回True，否则返回False
    """
    try:
        datetime(year=year, month=month, day=day)
        return True
    except ValueError:
        return False

def getAge(
    birthDate: datetime,
    atDate: Optional[datetime] = None
) -> Tuple[int, int, int]:
    """
    计算年龄(年,月,日)
    
    Args:
        birthDate: 出生日期
        atDate: 计算日期(默认当前日期)
        
    Returns:
        包含(年,月,日)的元组
    """
    atDate = atDate or datetime.now()
    
    years = atDate.year - birthDate.year
    months = atDate.month - birthDate.month
    days = atDate.day - birthDate.day
    
    if days < 0:
        months -= 1
        days += calendar.monthrange(atDate.year, atDate.month)[1]
    if months < 0:
        years -= 1
        months += 12
        
    return (years, months, days)