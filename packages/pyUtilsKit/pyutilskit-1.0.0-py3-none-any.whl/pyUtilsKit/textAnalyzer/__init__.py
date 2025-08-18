"""
textAnalyzer - 一组用于文本分析的实用函数
"""

import re
import math
from collections import Counter
from typing import List, Dict, Set, Optional

def cleanText(text: str, removePunct: bool = True) -> str:
    """
    清理和标准化文本
    
    Args:
        text: 要清理的原始文本
        removePunct: 是否移除标点符号
        
    Returns:
        清理后的文本
    """
    cleaned = text.lower().strip()
    if removePunct:
        cleaned = re.sub(r'[^\w\s]', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned

def countWords(text: str) -> int:
    """
    计算文本中的单词数量
    
    Args:
        text: 输入文本
        
    Returns:
        单词数量
        
    Raises:
        ValueError: 如果输入文本为空
    """
    if not text.strip():
        raise ValueError("输入文本不能为空")
    return len(cleanText(text).split())

def countChars(text: str, includeSpaces: bool = False) -> int:
    """
    计算文本中的字符数量
    
    Args:
        text: 输入文本
        includeSpaces: 是否包含空格
        
    Returns:
        字符数量
    """
    return len(text) if includeSpaces else len(text.replace(' ', ''))

def getWordFrequencies(text: str, topN: Optional[int] = None) -> Dict[str, int]:
    """
    获取文本中单词的频率统计
    
    Args:
        text: 输入文本
        topN: 返回前N个高频词
        
    Returns:
        单词及其频率的字典
    """
    words = cleanText(text).split()
    freq = Counter(words)
    return dict(freq.most_common(topN)) if topN else dict(freq)

def calculateReadingTime(text: str, wpm: int = 200) -> float:
    """
    估算文本的阅读时间(分钟)
    
    Args:
        text: 输入文本
        wpm: 每分钟阅读单词数
        
    Returns:
        预估阅读时间(分钟)
    """
    wordCount = countWords(text)
    return max(0.1, round(wordCount / wpm, 2))

def calculateTextSimilarity(
    text1: str,
    text2: str
) -> float:
    """
    计算两段文本的余弦相似度
    
    Args:
        text1: 第一段文本
        text2: 第二段文本
        
    Returns:
        相似度得分(0-1之间)
        
    Raises:
        ValueError: 如果任一输入文本为空
    """
    if not text1.strip() or not text2.strip():
        raise ValueError("输入文本不能为空")
        
    vec1 = Counter(cleanText(text1).split())
    vec2 = Counter(cleanText(text2).split())
    
    common = set(vec1.keys()) & set(vec2.keys())
    dot = sum(vec1[w] * vec2[w] for w in common)
    
    mag1 = math.sqrt(sum(c**2 for c in vec1.values()))
    mag2 = math.sqrt(sum(c**2 for c in vec2.values()))
    
    return dot / (mag1 * mag2) if mag1 and mag2 else 0.0

def extractKeywords(
    text: str,
    stopWords: Optional[Set[str]] = None,
    minLength: int = 3
) -> List[str]:
    """
    从文本中提取关键词
    
    Args:
        text: 输入文本
        stopWords: 要排除的停用词集合
        minLength: 关键词最小长度
        
    Returns:
        按频率排序的关键词列表
    """
    stopWords = stopWords or set()
    words = [w for w in cleanText(text).split() 
            if len(w) >= minLength and w not in stopWords]
    return [w for w, _ in Counter(words).most_common()]

def splitIntoSentences(text: str) -> List[str]:
    """
    将文本分割成句子
    
    Args:
        text: 输入文本
        
    Returns:
        句子列表
    """
    return [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]

def calculateLexicalDiversity(text: str) -> float:
    """
    计算文本的词汇多样性(唯一词数/总词数)
    
    Args:
        text: 输入文本
        
    Returns:
        词汇多样性得分
    """
    words = cleanText(text).split()
    return len(set(words)) / len(words) if words else 0.0

def getSentimentScore(
    text: str,
    positiveWords: Optional[Set[str]] = None,
    negativeWords: Optional[Set[str]] = None
) -> float:
    """
    计算文本的情感倾向得分(-1到1之间)
    
    Args:
        text: 输入文本
        positiveWords: 积极词汇集合
        negativeWords: 消极词汇集合
        
    Returns:
        情感得分
    """
    pos = positiveWords or {'good', 'great', 'love', 'happy'}
    neg = negativeWords or {'bad', 'hate', 'terrible', 'sad'}
    
    words = set(cleanText(text).split())
    posCnt = len(words & pos)
    negCnt = len(words & neg)
    
    return (posCnt - negCnt) / (posCnt + negCnt) if (posCnt or negCnt) else 0.0