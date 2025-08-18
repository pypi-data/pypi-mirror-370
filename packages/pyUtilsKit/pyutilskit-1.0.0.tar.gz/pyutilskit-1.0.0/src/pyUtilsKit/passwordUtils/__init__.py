"""
passwordUtils - 一个用于密码生成和验证的Python工具库，提供密码生成、强度验证等功能。
"""

import random
import string
from typing import Union

def genPass(length: int = 12, useDigits: bool = True, useSpecialChars: bool = True) -> str:
    """
    生成随机密码
    
    Args:
        length: 密码长度，默认为12
        useDigits: 是否包含数字，默认为True
        useSpecialChars: 是否包含特殊字符，默认为True
        
    Returns:
        str: 生成的随机密码
        
    Raises:
        ValueError: 如果length小于4或大于50
    """
    if length < 4:
        raise ValueError("密码长度不能小于4")
    if length > 50:
        raise ValueError("密码长度不能大于50")
        
    chars = string.ascii_letters
    if useDigits:
        chars += string.digits
    if useSpecialChars:
        chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
    while True:
        password = ''.join(random.choice(chars) for _ in range(length))
        if checkPassStrength(password) >= 2:  # 确保生成的密码至少有中等强度
            return password

def checkPassStrength(password: str) -> int:
    """
    检查密码强度
    
    Args:
        password: 要检查的密码字符串
        
    Returns:
        int: 密码强度等级 (0-弱, 1-中, 2-强, 3-非常强)
        
    Raises:
        ValueError: 如果密码为空
    """
    if not password:
        raise ValueError("密码不能为空")
        
    # 检查字符类型
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    char_types = sum([has_lower, has_upper, has_digit, has_special])
    
    if len(password) < 8 or char_types < 2:
        return 0
    elif len(password) < 12 and char_types >= 2:
        return 1
    elif char_types == 3:
        return 2
    else:
        return 3

def encryptPass(password: str, key: Union[str, int] = "secret") -> str:
    """
    简单密码加密 (请勿在正式项目中使用)
    
    Args:
        password: 要加密的密码
        key: 加密密钥，可以是字符串或整数，默认为"secret"
        
    Returns:
        str: 加密后的字符串
        
    Raises:
        ValueError: 如果密码或密钥为空
    """
    if not password:
        raise ValueError("密码不能为空")
    if not key:
        raise ValueError("密钥不能为空")
        
    if isinstance(key, int):
        key = str(key)
        
    password_bytes = password.encode('utf-8')
    key_bytes = key.encode('utf-8')
    
    encrypted_bytes = bytearray()
    key_len = len(key_bytes)
    for i, byte in enumerate(password_bytes):
        key_byte = key_bytes[i % key_len]
        encrypted_byte = (byte + key_byte) % 256
        encrypted_bytes.append(encrypted_byte)
        
    return encrypted_bytes.decode('latin-1')

def decryptPass(encrypted: str, key: Union[str, int] = "secret") -> str:
    """
    解密密码(与encryptPass配套使用) (请勿在正式项目中使用)
    
    Args:
        encrypted: 加密后的字符串
        key: 解密密钥，必须与加密时使用的相同
        
    Returns:
        str: 解密后的原始密码
        
    Raises:
        ValueError: 如果加密字符串或密钥为空
    """
    if not encrypted:
        raise ValueError("加密字符串不能为空")
    if not key:
        raise ValueError("密钥不能为空")
        
    if isinstance(key, int):
        key = str(key)
    
    # 将加密字符串编码为字节
    encrypted_bytes = encrypted.encode('latin-1')
    key_bytes = key.encode('utf-8')
    
    decrypted_bytes = bytearray()
    key_len = len(key_bytes)
    for i, byte in enumerate(encrypted_bytes):
        key_byte = key_bytes[i % key_len]
        decrypted_byte = (byte - key_byte) % 256
        decrypted_bytes.append(decrypted_byte)
        
    return decrypted_bytes.decode('utf-8')

def isCommonPassword(password: str) -> bool:
    """
    检查密码是否是常见弱密码
    
    Args:
        password: 要检查的密码
        
    Returns:
        bool: 如果是常见密码返回True，否则返回False
        
    Raises:
        ValueError: 如果密码为空
    """
    if not password:
        raise ValueError("密码不能为空")
        
    commonPasswords = {
        '123456', 'password', '12345678', 'qwerty', '123456789',
        '12345', '1234', '111111', '1234567', 'dragon',
        '123123', 'baseball', 'abc123', 'football', 'monkey',
        'letmein', 'shadow', 'master', '666666', 'qwertyuiop'
    }
    
    return password.lower() in commonPasswords

def genPassPhrase(wordCount: int = 4, separator: str = '-', capitalize: bool = True) -> str:
    """
    生成易记的密码短语
    
    Args:
        wordCount: 包含的单词数量，默认为4
        separator: 单词分隔符，默认为'-'
        capitalize: 是否大写每个单词的首字母，默认为True
        
    Returns:
        str: 生成的密码短语
        
    Raises:
        ValueError: 如果wordCount小于2或大于8
    """
    if wordCount < 2:
        raise ValueError("单词数量不能小于2")
    if wordCount > 8:
        raise ValueError("单词数量不能大于8")
        
    wordList = [
        'apple', 'banana', 'carrot', 'dog', 'elephant', 'flower', 'giraffe',
        'house', 'island', 'jungle', 'kite', 'lion', 'mountain', 'notebook',
        'ocean', 'pencil', 'queen', 'river', 'sun', 'tree', 'umbrella', 'volcano',
        'water', 'xylophone', 'yellow', 'zebra'
    ]
    
    words = random.sample(wordList, wordCount)
    if capitalize:
        words = [word.capitalize() for word in words]
        
    return separator.join(words)