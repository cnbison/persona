"""
文本处理工具
提供中文分词、文本清洗、关键词提取、文本分段等功能
"""
import re
import string
from typing import List, Optional, Tuple
from loguru import logger

# 尝试导入NLP库
try:
    import jieba
    import jieba.analyse
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False
    logger.warning("⚠️  jieba未安装，部分功能将受限")

try:
    import spacy
    SPACY_AVAILABLE = True
    # 尝试加载中文模型
    try:
        nlp = spacy.load("zh_core_web_sm")
    except OSError:
        logger.warning("⚠️  spaCy中文模型未找到，请运行: python -m spacy download zh_core_web_sm")
        SPACY_AVAILABLE = False
        nlp = None
except ImportError:
    SPACY_AVAILABLE = False
    nlp = None
    logger.warning("⚠️  spaCy未安装，部分功能将受限")


class TextProcessor:
    """
    文本处理工具类

    功能：
    - 中文分词
    - 文本清洗
    - 关键词提取
    - 文本分段
    - 关键句提取
    """

    def __init__(self):
        """初始化文本处理器"""
        self.jieba_initialized = False

        if JIEBA_AVAILABLE:
            # 设置jieba日志级别
            import jieba
            jieba.setLogLevel(jieba.logging.INFO)
            self.jieba_initialized = True
            logger.info("✅ jieba初始化成功")

        if SPACY_AVAILABLE and nlp:
            self.nlp = nlp
            logger.info("✅ spaCy初始化成功")

    def clean_text(self, text: str) -> str:
        """
        清洗文本

        去除：
        - 多余空白字符
        - 特殊符号（保留中文标点）
        - HTML标签
        - 页码
        """
        if not text:
            return ""

        # 去除HTML标签
        text = re.sub(r'<[^>]+>', '', text)

        # 去除页码（如"第123页"、"- 124 -"等模式）
        text = re.sub(r'第\s*\d+\s*页', '', text)
        text = re.sub(r'-\s*\d+\s*-', '', text)

        # 统一换行符
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        # 去除多余空行（超过2个连续换行）
        text = re.sub(r'\n{3,}', '\n\n', text)

        # 去除行首行尾空白
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)

        # 去除首尾空白
        text = text.strip()

        return text

    def remove_redundant_info(self, text: str) -> str:
        """
        去除著作中的冗余信息

        去除：
        - 版权声明
        - ISBN信息
        - 出版信息
        - 责任编辑等
        """
        if not text:
            return ""

        # 版权声明模式
        copyright_patterns = [
            r'版权所有.*?[保留|所有]',
            r'Copyright\s*©.*?\d{4}',
            r'ISBN\s*[\d-]+',
            r'责任编辑\s*[:：].*',
            r'封面设计\s*[:：].*',
            r'出版发行\s*[:：].*',
            r'印刷\s*[:：].*',
            r'版次\s*[:：].*',
            r'印次\s*[:：].*',
        ]

        for pattern in copyright_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)

        # 去除多余空行
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text.strip()

    def segment_chinese(self, text: str) -> List[str]:
        """
        中文分词

        返回: 分词列表
        """
        if not self.jieba_initialized:
            logger.warning("⚠️  jieba未初始化，返回空列表")
            return []

        words = jieba.lcut(text)
        # 过滤单字和标点
        words = [w for w in words if len(w) > 1 and w not in string.punctuation]
        return words

    def extract_keywords(
        self,
        text: str,
        top_k: int = 20,
        with_weight: bool = False
    ) -> List[str] | List[Tuple[str, float]]:
        """
        提取关键词

        参数:
            text: 文本
            top_k: 返回前k个关键词
            with_weight: 是否返回权重

        返回:
            如果with_weight=True: [("关键词", 0.5), ...]
            如果with_weight=False: ["关键词", ...]
        """
        if not self.jieba_initialized:
            logger.warning("⚠️  jieba未初始化，返回空列表")
            return [] if not with_weight else []

        if with_weight:
            keywords = jieba.analyse.extract_tags(text, topK=top_k, withWeight=True)
        else:
            keywords = jieba.analyse.extract_tags(text, topK=top_k, withWeight=False)

        return keywords

    def split_text_by_paragraph(self, text: str) -> List[str]:
        """
        按段落分割文本

        返回: 段落列表
        """
        if not text:
            return []

        # 按换行符分割
        paragraphs = text.split('\n')

        # 过滤空段落
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        return paragraphs

    def split_text_by_sentence(self, text: str) -> List[str]:
        """
        按句子分割文本

        返回: 句子列表
        """
        if not text:
            return []

        if SPACY_AVAILABLE and self.nlp:
            # 使用spaCy分句
            doc = self.nlp(text)
            sentences = [sent.text.strip() for sent in doc.sents]
        else:
            # 简单的正则表达式分句
            # 匹配中文句号、问号、感叹号
            sentences = re.split(r'[。！？；]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]

        return sentences

    def extract_key_sentences(
        self,
        text: str,
        top_k: int = 5,
        window_size: int = 3
    ) -> List[Tuple[str, int]]:
        """
        提取关键句（基于TextRank简化版）

        参数:
            text: 文本
            top_k: 返回前k个句子
            window_size: 窗口大小

        返回:
            [(句子, 重要性分数), ...]
        """
        if not text:
            return []

        # 分句
        sentences = self.split_text_by_sentence(text)

        if len(sentences) <= top_k:
            # 如果句子数量少于top_k，全部返回
            return [(s, 1.0) for s in sentences]

        # 简化的TextRank算法
        # 1. 分词并过滤停用词
        word_lists = []
        for sent in sentences:
            words = self.segment_chinese(sent)
            word_lists.append(words)

        # 2. 构建词共现矩阵
        from collections import defaultdict
        word_freq = defaultdict(int)

        for words in word_lists:
            unique_words = set(words)
            for word in unique_words:
                word_freq[word] += 1

        # 3. 计算句子得分
        sentence_scores = []
        for i, words in enumerate(word_lists):
            score = sum(word_freq[w] for w in words)
            # 归一化
            score = score / max(len(words), 1)
            sentence_scores.append((sentences[i], score))

        # 4. 排序并返回top_k
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        return sentence_scores[:top_k]

    def truncate_text(
        self,
        text: str,
        max_length: int = 1000,
        suffix: str = "..."
    ) -> str:
        """
        截断文本到指定长度

        尝试在句子边界截断，避免截断句子中间
        """
        if len(text) <= max_length:
            return text

        # 在最大长度附近寻找最近的句号
        truncated = text[:max_length]
        last_period = truncated.rfind('。')

        if last_period > max_length * 0.8:  # 如果句号位置在80%之后
            return text[:last_period + 1]
        else:
            return truncated + suffix

    def count_words(self, text: str) -> int:
        """
        统计字数（中文字符+英文单词）

        中文按字符计，英文按单词计
        """
        if not text:
            return 0

        # 统计中文字符
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))

        # 统计英文单词
        english_text = re.sub(r'[\u4e00-\u9fff]', ' ', text)
        english_words = len(english_text.split())

        return chinese_chars + english_words

    def detect_language(self, text: str) -> str:
        """
        检测文本主要语言

        返回: 'zh' (中文), 'en' (英文), 'mixed' (混合)
        """
        if not text:
            return 'unknown'

        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        total_chars = len(text)

        if chinese_chars / total_chars > 0.3:
            return 'zh'
        elif chinese_chars / total_chars < 0.1:
            return 'en'
        else:
            return 'mixed'


# 全局单例
_text_processor: Optional[TextProcessor] = None


def get_text_processor() -> TextProcessor:
    """获取文本处理器单例"""
    global _text_processor
    if _text_processor is None:
        _text_processor = TextProcessor()
    return _text_processor


if __name__ == "__main__":
    # 测试代码
    processor = get_text_processor()

    # 测试文本
    test_text = """
    这是一个测试文本。用于测试文本处理器的各项功能。

    本测试包含多个段落，以及一些特殊符号：@#$%^&*()。
    还包含一些数字：123456。

    ISBN 978-7-123-45678-9
    版权所有 © 2025

    Python是一种广泛使用的编程语言。它简洁易读，功能强大。
    许多开发者喜欢使用Python进行开发。
    """

    print("=" * 50)
    print("测试文本清洗")
    print("=" * 50)
    cleaned = processor.clean_text(test_text)
    print(cleaned)

    print("\n" + "=" * 50)
    print("测试去除冗余信息")
    print("=" * 50)
    no_redundant = processor.remove_redundant_info(test_text)
    print(no_redundant)

    print("\n" + "=" * 50)
    print("测试关键词提取")
    print("=" * 50)
    keywords = processor.extract_keywords(cleaned, top_k=10)
    print(keywords)

    print("\n" + "=" * 50)
    print("测试统计字数")
    print("=" * 50)
    word_count = processor.count_words(cleaned)
    print(f"字数: {word_count}")

    print("\n" + "=" * 50)
    print("测试语言检测")
    print("=" * 50)
    lang = processor.detect_language(cleaned)
    print(f"语言: {lang}")
