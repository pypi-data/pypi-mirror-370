"""
stringProcessor - 提供各种字符串处理功能的工具库
"""

import re

import hashlib
from typing import List

def toCamelCase(inputStr: str) -> str:
    """
    将下划线或空格分隔的字符串转换为驼峰式
    
    Args:
        inputStr: 输入字符串
        
    Returns:
        转换后的驼峰式字符串
    """
    words = re.split(r'[_\s]+', inputStr)
    return words[0].lower() + ''.join(word.capitalize() for word in words[1:])

def toSnakeCase(inputStr: str) -> str:
    """
    将驼峰式字符串转换为下划线分隔
    
    Args:
        inputStr: 输入字符串
        
    Returns:
        转换后的下划线分隔字符串
    """
    return re.sub(r'(?<!^)(?=[A-Z])', '_', inputStr).lower()

def truncateString(
    inputStr: str,
    maxLength: int,
    ellipsis: str = "..."
) -> str:
    """
    截断字符串并在末尾添加省略号
    
    Args:
        inputStr: 输入字符串
        maxLength: 最大长度(包含省略号)
        ellipsis: 省略符号
        
    Returns:
        截断后的字符串
        
    Raises:
        ValueError: 如果maxLength小于省略号长度
    """
    if maxLength < len(ellipsis):
        raise ValueError("maxLength不能小于省略号长度")
    return (inputStr[:maxLength - len(ellipsis)] + ellipsis) if len(inputStr) > maxLength else inputStr

def countSubstring(
    mainStr: str,
    subStr: str,
    caseSensitive: bool = True
) -> int:
    """
    计算子字符串出现的次数
    
    Args:
        mainStr: 主字符串
        subStr: 要查找的子字符串
        caseSensitive: 是否区分大小写
        
    Returns:
        子字符串出现的次数
    """
    if not caseSensitive:
        mainStr = mainStr.lower()
        subStr = subStr.lower()
    return mainStr.count(subStr)

def md5Hash(inputStr: str) -> str:
    """
    计算字符串的MD5哈希值
    
    Args:
        inputStr: 输入字符串
        
    Returns:
        MD5哈希值的十六进制表示
    """
    return hashlib.md5(inputStr.encode('utf-8')).hexdigest()

def base64Encode(inputStr: str) -> str:
    """
    对字符串进行Base64编码
    
    Args:
        inputStr: 输入字符串
        
    Returns:
        Base64编码后的字符串
    """
    import base64
    return base64.b64encode(inputStr.encode('utf-8')).decode('utf-8')

def base64Decode(encodedStr: str) -> str:
    """
    对Base64编码的字符串进行解码
    
    Args:
        encodedStr: Base64编码的字符串
        
    Returns:
        解码后的原始字符串
        
    Raises:
        ValueError: 如果输入不是有效的Base64字符串
    """
    import base64
    try:
        return base64.b64decode(encodedStr.encode('utf-8')).decode('utf-8')
    except Exception:
        raise ValueError("无效的Base64输入")

def splitIntoChunks(
    inputStr: str,
    chunkSize: int
) -> List[str]:
    """
    将字符串分割成指定大小的块
    
    Args:
        inputStr: 输入字符串
        chunkSize: 每个块的大小
        
    Returns:
        分割后的字符串列表
        
    Raises:
        ValueError: 如果chunkSize小于1
    """
    if chunkSize < 1:
        raise ValueError("chunkSize必须大于0")
    return [inputStr[i:i+chunkSize] for i in range(0, len(inputStr), chunkSize)]

def removeDuplicates(inputStr: str) -> str:
    """
    移除字符串中的重复字符
    
    Args:
        inputStr: 输入字符串
        
    Returns:
        去重后的字符串
    """
    seen = set()
    return ''.join([char for char in inputStr if not (char in seen or seen.add(char))])

def isPalindrome(inputStr: str) -> bool:
    """
    检查字符串是否是回文
    
    Args:
        inputStr: 输入字符串
        
    Returns:
        如果是回文返回True，否则返回False
    """
    cleaned = re.sub(r'[^a-zA-Z0-9]', '', inputStr.lower())
    return cleaned == cleaned[::-1]

def reverseWords(inputStr: str) -> str:
    """
    反转字符串中的单词顺序
    
    Args:
        inputStr: 输入字符串
        
    Returns:
        单词顺序反转后的字符串
    """
    return ' '.join(inputStr.split()[::-1])