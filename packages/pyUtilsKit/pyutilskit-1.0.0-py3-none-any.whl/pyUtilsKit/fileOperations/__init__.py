"""
fileOperations - 提供各种文件操作功能的工具库
"""

import os
import hashlib
import zipfile
import shutil
from typing import Optional, List, Tuple, Union

def readFile(filePath: str) -> str:
    """
    读取文件内容
    
    Args:
        filePath: 文件路径
        
    Returns:
        文件内容字符串
        
    Raises:
        FileNotFoundError: 如果文件不存在
        IOError: 如果读取文件失败
    """
    if not os.path.exists(filePath):
        raise FileNotFoundError(f"文件不存在: {filePath}")
    with open(filePath, 'r', encoding='utf-8') as f:
        return f.read()

def writeFile(
    filePath: str,
    content: str,
    overwrite: bool = False
) -> bool:
    """
    写入内容到文件
    
    Args:
        filePath: 文件路径
        content: 要写入的内容
        overwrite: 是否覆盖已存在文件
        
    Returns:
        写入成功返回True，否则返回False
        
    Raises:
        FileExistsError: 如果文件已存在且不覆盖
        IOError: 如果写入文件失败
    """
    if os.path.exists(filePath) and not overwrite:
        raise FileExistsError(f"文件已存在: {filePath}")
    with open(filePath, 'w', encoding='utf-8') as f:
        f.write(content)
    return True

def getFileInfo(filePath: str) -> Tuple[str, int, float]:
    """
    获取文件基本信息
    
    Args:
        filePath: 文件路径
        
    Returns:
        包含(文件名, 文件大小(字节), 最后修改时间戳)的元组
        
    Raises:
        FileNotFoundError: 如果文件不存在
    """
    if not os.path.exists(filePath):
        raise FileNotFoundError(f"文件不存在: {filePath}")
    stat = os.stat(filePath)
    return (os.path.basename(filePath), stat.st_size, stat.st_mtime)

def calculateFileHash(
    filePath: str,
    algorithm: str = 'md5'
) -> str:
    """
    计算文件哈希值
    
    Args:
        filePath: 文件路径
        algorithm: 哈希算法(md5/sha1/sha256)
        
    Returns:
        文件哈希值的十六进制字符串
        
    Raises:
        ValueError: 如果算法不支持
        FileNotFoundError: 如果文件不存在
    """
    if algorithm not in ['md5', 'sha1', 'sha256']:
        raise ValueError("不支持的哈希算法")
    if not os.path.exists(filePath):
        raise FileNotFoundError(f"文件不存在: {filePath}")
    
    hashFunc = getattr(hashlib, algorithm)()
    with open(filePath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hashFunc.update(chunk)
    return hashFunc.hexdigest()

def createDirectory(
    dirPath: str,
    parents: bool = True
) -> bool:
    """
    创建目录
    
    Args:
        dirPath: 目录路径
        parents: 是否创建父目录
        
    Returns:
        创建成功返回True，否则返回False
        
    Raises:
        FileExistsError: 如果目录已存在
    """
    if os.path.exists(dirPath):
        raise FileExistsError(f"目录已存在: {dirPath}")
    os.makedirs(dirPath, exist_ok=parents)
    return True

def listFiles(
    dirPath: str,
    recursive: bool = False,
    extensions: Optional[List[str]] = None
) -> List[str]:
    """
    列出目录中的文件
    
    Args:
        dirPath: 目录路径
        recursive: 是否递归列出子目录
        extensions: 要筛选的文件扩展名列表
        
    Returns:
        文件路径列表
        
    Raises:
        NotADirectoryError: 如果不是目录
    """
    if not os.path.isdir(dirPath):
        raise NotADirectoryError(f"不是目录: {dirPath}")
    
    files = []
    if recursive:
        for root, _, filenames in os.walk(dirPath):
            for filename in filenames:
                if extensions is None or any(filename.endswith(ext) for ext in extensions):
                    files.append(os.path.join(root, filename))
    else:
        for item in os.listdir(dirPath):
            fullPath = os.path.join(dirPath, item)
            if os.path.isfile(fullPath) and (extensions is None or any(item.endswith(ext) for ext in extensions)):
                files.append(fullPath)
    return files

def zipFiles(
    zipPath: str,
    filePaths: List[str],
    compression: int = zipfile.ZIP_DEFLATED
) -> bool:
    """
    压缩多个文件到ZIP
    
    Args:
        zipPath: 目标ZIP文件路径
        filePaths: 要压缩的文件路径列表
        compression: 压缩方法
        
    Returns:
        压缩成功返回True，否则返回False
        
    Raises:
        ValueError: 如果没有文件要压缩
        FileNotFoundError: 如果任何源文件不存在
    """
    if not filePaths:
        raise ValueError("没有文件要压缩")
    for filePath in filePaths:
        if not os.path.exists(filePath):
            raise FileNotFoundError(f"文件不存在: {filePath}")
    
    with zipfile.ZipFile(zipPath, 'w', compression) as zipf:
        for filePath in filePaths:
            zipf.write(filePath, os.path.basename(filePath))
    return True

def unzipFile(
    zipPath: str,
    extractPath: str,
    overwrite: bool = False
) -> List[str]:
    """
    解压ZIP文件
    
    Args:
        zipPath: ZIP文件路径
        extractPath: 解压目标路径
        overwrite: 是否覆盖已存在文件
        
    Returns:
        解压出的文件路径列表
        
    Raises:
        FileNotFoundError: 如果ZIP文件不存在
        zipfile.BadZipFile: 如果不是有效的ZIP文件
    """
    if not os.path.exists(zipPath):
        raise FileNotFoundError(f"ZIP文件不存在: {zipPath}")
    
    extractedFiles = []
    with zipfile.ZipFile(zipPath, 'r') as zipf:
        for member in zipf.namelist():
            targetPath = os.path.join(extractPath, member)
            if os.path.exists(targetPath) and not overwrite:
                continue
            zipf.extract(member, extractPath)
            extractedFiles.append(targetPath)
    return extractedFiles

def copyFile(
    srcPath: str,
    dstPath: str,
    overwrite: bool = False
) -> bool:
    """
    复制文件
    
    Args:
        srcPath: 源文件路径
        dstPath: 目标文件路径
        overwrite: 是否覆盖已存在文件
        
    Returns:
        复制成功返回True，否则返回False
        
    Raises:
        FileNotFoundError: 如果源文件不存在
        FileExistsError: 如果目标文件已存在且不覆盖
    """
    if not os.path.exists(srcPath):
        raise FileNotFoundError(f"源文件不存在: {srcPath}")
    if os.path.exists(dstPath) and not overwrite:
        raise FileExistsError(f"目标文件已存在: {dstPath}")
    shutil.copy2(srcPath, dstPath)
    return True

def deleteFile(filePath: str) -> bool:
    """
    删除文件
    
    Args:
        filePath: 文件路径
        
    Returns:
        删除成功返回True，否则返回False
        
    Raises:
        FileNotFoundError: 如果文件不存在
    """
    if not os.path.exists(filePath):
        raise FileNotFoundError(f"文件不存在: {filePath}")
    os.remove(filePath)
    return True