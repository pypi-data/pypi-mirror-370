"""
httpUtils - 提供HTTP请求相关功能的工具库
"""

import requests
from urllib.parse import parse_qsl
from typing import Optional, Dict, Any, Union
from requests.exceptions import RequestException

def getRequest(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 10
) -> requests.Response:
    """
    发送GET请求
    
    Args:
        url: 请求URL
        params: 查询参数
        headers: 请求头
        timeout: 超时时间(秒)
        
    Returns:
        requests.Response对象
        
    Raises:
        RequestException: 如果请求失败
        ValueError: 如果URL无效
    """
    if not url.startswith(('http://', 'https://')):
        raise ValueError("无效的URL格式")
    
    try:
        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=timeout
        )
        response.raise_for_status()
        return response
    except RequestException as e:
        raise RequestException(f"GET请求失败: {str(e)}")

def postRequest(
    url: str,
    data: Optional[Union[Dict[str, Any], str]] = None,
    json: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 10
) -> requests.Response:
    """
    发送POST请求
    
    Args:
        url: 请求URL
        data: 表单数据
        json: JSON数据
        headers: 请求头
        timeout: 超时时间(秒)
        
    Returns:
        requests.Response对象
        
    Raises:
        RequestException: 如果请求失败
        ValueError: 如果URL无效或同时提供了data和json
    """
    if not url.startswith(('http://', 'https://')):
        raise ValueError("无效的URL格式")
    if data is not None and json is not None:
        raise ValueError("不能同时提供data和json参数")
    
    try:
        response = requests.post(
            url,
            data=data,
            json=json,
            headers=headers,
            timeout=timeout
        )
        response.raise_for_status()
        return response
    except RequestException as e:
        raise RequestException(f"POST请求失败: {str(e)}")

def getJsonResponse(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 10
) -> Dict[str, Any]:
    """
    发送GET请求并返回JSON响应
    
    Args:
        url: 请求URL
        params: 查询参数
        headers: 请求头
        timeout: 超时时间(秒)
        
    Returns:
        解析后的JSON数据
        
    Raises:
        RequestException: 如果请求失败
        ValueError: 如果响应不是有效的JSON
    """
    response = getRequest(url, params, headers, timeout)
    try:
        return response.json()
    except ValueError as e:
        raise ValueError(f"无效的JSON响应: {str(e)}")

def postJsonResponse(
    url: str,
    jsonData: Dict[str, Any],
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 10
) -> Dict[str, Any]:
    """
    发送POST请求(JSON数据)并返回JSON响应
    
    Args:
        url: 请求URL
        jsonData: 要发送的JSON数据
        headers: 请求头
        timeout: 超时时间(秒)
        
    Returns:
        解析后的JSON数据
        
    Raises:
        RequestException: 如果请求失败
        ValueError: 如果响应不是有效的JSON
    """
    response = postRequest(url, json=jsonData, headers=headers, timeout=timeout)
    try:
        return response.json()
    except ValueError as e:
        raise ValueError(f"无效的JSON响应: {str(e)}")

def downloadFile(
    url: str,
    savePath: str,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 30
) -> bool:
    """
    下载文件
    
    Args:
        url: 文件URL
        savePath: 保存路径
        headers: 请求头
        timeout: 超时时间(秒)
        
    Returns:
        下载成功返回True，否则返回False
        
    Raises:
        RequestException: 如果下载失败
        IOError: 如果保存文件失败
    """
    try:
        response = getRequest(url, headers=headers, timeout=timeout)
        with open(savePath, 'wb') as f:
            f.write(response.content)
        return True
    except IOError as e:
        raise IOError(f"保存文件失败: {str(e)}")

def setDefaultHeaders(
    headers: Dict[str, str]
) -> None:
    """
    设置默认请求头
    
    Args:
        headers: 要设置的默认请求头
        
    Returns:
        None
    """
    requests.session().headers.update(headers)

def getResponseHeaders(
    url: str,
    timeout: int = 5
) -> Dict[str, str]:
    """
    获取响应头(HEAD请求)
    
    Args:
        url: 请求URL
        timeout: 超时时间(秒)
        
    Returns:
        响应头字典
        
    Raises:
        RequestException: 如果请求失败
    """
    try:
        response = requests.head(url, timeout=timeout)
        return dict(response.headers)
    except RequestException as e:
        raise RequestException(f"获取响应头失败: {str(e)}")

def checkUrlStatus(
    url: str,
    timeout: int = 5
) -> int:
    """
    检查URL状态码
    
    Args:
        url: 要检查的URL
        timeout: 超时时间(秒)
        
    Returns:
        HTTP状态码
        
    Raises:
        RequestException: 如果请求失败
    """
    try:
        response = requests.head(url, timeout=timeout)
        return response.status_code
    except RequestException as e:
        raise RequestException(f"检查URL状态失败: {str(e)}")

def addQueryParams(
    url: str,
    params: Dict[str, Any]
) -> str:
    """
    向URL添加查询参数
    
    Args:
        url: 原始URL
        params: 要添加的查询参数
        
    Returns:
        添加参数后的完整URL
        
    Raises:
        ValueError: 如果URL无效
    """
    if not url.startswith(('http://', 'https://')):
        raise ValueError("无效的URL格式")
    
    from urllib.parse import urlencode, urlparse, urlunparse
    parsed = urlparse(url)
    query = dict(parse_qsl(parsed.query))
    query.update(params)
    newQuery = urlencode(query)
    return urlunparse(parsed._replace(query=newQuery))