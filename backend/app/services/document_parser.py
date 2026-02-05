"""
文档解析服务
负责解析各种格式的著作文件，提取结构化内容
"""
import re
from collections import Counter
from pathlib import Path
from typing import Optional, List, Dict
from loguru import logger
import uuid

from app.models.book import Book, Chapter, CoreViewpoint
from app.utils.text_processor import get_text_processor
from app.utils.file_handler import get_file_handler

# 尝试导入文档解析库
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    logger.warning("⚠️  pdfplumber未安装，PDF解析功能不可用")

try:
    import ebooklib
    from ebooklib import epub
    EBOOKLIB_AVAILABLE = True
except ImportError:
    EBOOKLIB_AVAILABLE = False
    logger.warning("⚠️  ebooklib未安装，EPUB解析功能不可用")

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    logger.warning("⚠️  python-docx未安装，DOCX解析功能不可用")


class DocumentParser:
    """
    文档解析服务

    功能：
    - 解析PDF、EPUB、TXT、DOCX格式
    - 识别章节结构
    - 提取核心观点
    - 结构化存储
    """

    def __init__(self):
        """初始化文档解析器"""
        self.text_processor = get_text_processor()
        self.file_handler = get_file_handler()
        logger.info("✅ 文档解析服务初始化成功")

    async def parse_book(
        self,
        file_path: str,
        title: Optional[str] = None,
        author: Optional[str] = None
    ) -> Book:
        """
        解析著作文件

        参数:
            file_path: 文件路径
            title: 著作标题（可选，从文件名提取）
            author: 作者（可选）

        返回:
            Book对象
        """
        logger.info(f"📖 开始解析著作: {file_path}")

        # 获取文件信息
        file_info = self.file_handler.get_file_info(file_path)
        if not file_info:
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 确定文件类型
        file_ext = file_info['extension']

        # 提取文本内容
        if file_ext == 'pdf':
            text = await self._parse_pdf(file_path)
        elif file_ext == 'epub':
            text = await self._parse_epub(file_path)
        elif file_ext == 'txt':
            text = await self._parse_txt(file_path)
        elif file_ext == 'docx':
            text = await self._parse_docx(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_ext}")

        raw_text = text
        logger.info(f"✅ 文本提取完成，总字数: {len(text)}")

        # 清洗文本
        logger.info("🧹 开始清洗文本...")
        text = self.text_processor.clean_text(text)
        text = self.text_processor.remove_redundant_info(text)
        text = self._remove_repeated_lines(text)
        cleaned_lines = [line for line in text.split('\n') if line.strip()]
        raw_lines = [line for line in raw_text.split('\n') if line.strip()]
        logger.info(f"✅ 文本清洗完成，清洗后字数: {len(text)}")

        # 识别章节
        logger.info("📚 开始识别章节结构...")
        chapters, chapter_stats = self._identify_chapters(text, file_ext, title or Path(file_path).stem)
        logger.info(f"✅ 识别到 {len(chapters)} 个章节")

        # 提取核心观点
        logger.info("💡 开始提取核心观点...")
        core_viewpoints = await self._extract_core_viewpoints(chapters)
        logger.info(f"✅ 提取到 {len(core_viewpoints)} 个核心观点")

        # 创建Book对象
        parse_stats = {
            "raw_chars": len(raw_text),
            "cleaned_chars": len(text),
            "raw_lines": len(raw_lines),
            "cleaned_lines": len(cleaned_lines),
            "chapters_detected": len(chapters),
            "chapter_detection": chapter_stats
        }

        book = Book(
            book_id=str(uuid.uuid4()),
            title=title or Path(file_path).stem,
            author=author or "未知作者",
            language=self.text_processor.detect_language(text),
            file_path=file_path,
            file_type=file_ext,
            chapters=chapters,
            core_viewpoints=core_viewpoints,
            total_words=self.text_processor.count_words(text),
            parse_stats=parse_stats
        )

        logger.info(f"🎉 著作解析完成: {book.title}")
        return book

    async def _parse_pdf(self, file_path: str) -> str:
        """解析PDF文件"""
        if not PDFPLUMBER_AVAILABLE:
            raise ImportError("pdfplumber未安装，无法解析PDF文件")

        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"

                    if page_num % 10 == 0:
                        logger.debug(f"  已处理 {page_num + 1}/{len(pdf.pages)} 页")

        except Exception as e:
            logger.error(f"❌ PDF解析失败: {e}")
            raise

        return text

    async def _parse_epub(self, file_path: str) -> str:
        """解析EPUB文件"""
        if not EBOOKLIB_AVAILABLE:
            raise ImportError("ebooklib未安装，无法解析EPUB文件")

        try:
            book = epub.read_epub(file_path)
            text = ""

            # 获取所有章节
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    # 提取HTML内容
                    content = item.get_content()
                    # 简单的HTML标签去除
                    content = re.sub(r'<[^>]+>', '\n', content.decode('utf-8'))
                    text += content + "\n\n"

        except Exception as e:
            logger.error(f"❌ EPUB解析失败: {e}")
            raise

        return text

    async def _parse_txt(self, file_path: str) -> str:
        """解析TXT文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except UnicodeDecodeError:
            # 尝试其他编码
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    text = f.read()
            except:
                raise ValueError("无法解码文件，请确保文件编码为UTF-8或GBK")
        except Exception as e:
            logger.error(f"❌ TXT解析失败: {e}")
            raise

        return text

    async def _parse_docx(self, file_path: str) -> str:
        """解析DOCX文件"""
        if not DOCX_AVAILABLE:
            raise ImportError("python-docx未安装，无法解析DOCX文件")

        try:
            doc = docx.Document(file_path)
            paragraphs = []
            for paragraph in doc.paragraphs:
                content = paragraph.text.strip()
                if content:
                    paragraphs.append(content)
            return "\n\n".join(paragraphs)
        except Exception as e:
            logger.error(f"❌ DOCX解析失败: {e}")
            raise

    def _remove_repeated_lines(self, text: str) -> str:
        """移除重复页眉页脚等噪音行"""
        if not text:
            return text

        lines = [line.strip() for line in text.split('\n')]
        total = len(lines)
        counts = Counter([line for line in lines if line])

        def is_noise(line: str) -> bool:
            if not line:
                return False
            if re.match(r'^\d+$', line):
                return True
            if re.match(r'^-?\s*\d+\s*-?$', line):
                return True
            if re.match(r'^第?\s*\d+\s*页$', line):
                return True
            if re.match(r'^[IVXLCM]+$', line):
                return True
            if re.match(r'^[\W_]+$', line):
                return True
            return False

        filtered = []
        for line in lines:
            if not line:
                filtered.append("")
                continue
            if is_noise(line):
                continue
            if len(line) <= 30 and counts[line] >= 3 and (counts[line] / max(total, 1)) >= 0.05:
                continue
            filtered.append(line)

        return "\n".join(filtered).strip()

    def _identify_chapters(self, text: str, file_type: str, book_title: Optional[str] = None) -> tuple[List[Chapter], Dict]:
        """
        识别章节结构

        策略：
        1. 查找常见的章节标题模式
        2. 尝试匹配已知书籍的章节列表（如《乡土中国》）
        3. 按章节分割文本
        4. 为每个章节创建Chapter对象
        """
        chapters = []
        stats = {
            "strategy": "pattern",
            "patterns_matched": 0,
            "known_book_hit": None,
            "fallback": False
        }

        # 已知书籍的章节列表
        known_book_chapters = {
            '乡土中国': [
                '乡土本色',
                '文字下乡',
                '再论文字下乡',
                '差序格局',
                '系维着私人的道德',
                '家族',
                '男女有别',
                '礼治秩序',
                '无讼',
                '无为政治',
                '长老统治',
                '血缘和地缘',
                '名实的分离',
                '从欲望到需要'
            ],
            '论语': [
                '学而',
                '为政',
                '八佾',
                '里仁',
                '公冶长',
                '雍也',
                '述而',
                '泰伯',
                '子罕',
                '乡党',
                '先进',
                '颜渊',
                '子路',
                '宪问',
                '卫灵公',
                '季氏',
                '阳货',
                '微子',
                '子张',
                '尧曰'
            ]
        }

        chapter_patterns = [
            r'^第【\d+】段.*',  # "第【X】段：Y卷"（理想国格式）
            r'^第[一二三四五六七八九十百零\d]+章\s*',  # "第X章"
            r'^第[一二三四五六七八九十百零\d]+卷\s*',  # "第X卷"
            r'^第[一二三四五六七八九十百零\d]+篇\s*',  # "第X篇"（论语格式）
            r'^[\u4e00-\u9fff]{1,3}第[一二三四五六七八九十百零\d]+[卷篇章期]\s*',  # "学而第一卷"、"为政第二篇"（必须以卷/篇/章/期结尾）
            r'^[\u4e00-\u9fff]{1,3}第\d+[卷篇章期]\s*',  # "公冶长第五卷"、"先进第十一篇"（必须以卷/篇/章/期结尾）
            r'^Chapter\s*\d+',  # "Chapter X"
            r'^(Chapter|CHAPTER)\s+[IVXLC]+',  # "CHAPTER IV"
            r'^(Part|PART)\s+\d+',  # "Part 1"
            r'^(Part|PART)\s+[IVXLC]+',  # "PART II"
            r'^第[一二三四五六七八九十百零\d]+节\s*',  # "第X节"
            r'^[一二三四五六七八九十百零\d]+\.\s',  # "一. "、"1. "
            r'^[一二三四五六七八九十百零]+、\s',  # "一、"、"二、"
        ]

        def normalize_title(raw: str) -> str:
            if not raw:
                return ""
            cleaned = re.sub(r'[\s\u3000]+', '', raw)
            cleaned = re.sub(r'[·•\-\—\―\–\:\：\.\。]', '', cleaned)
            cleaned = re.sub(r'[章节卷篇]', '', cleaned)
            cleaned = cleaned.replace('第', '')
            return cleaned

        # 查找所有章节标题位置
        chapter_positions = []
        lines = text.split('\n')

        def is_noise_line(line: str) -> bool:
            if not line:
                return True
            if re.match(r'^[①②③④⑤⑥⑦⑧⑨⑩\[\d]]', line):
                return True
            if re.match(r'^\d+$', line):
                return True
            if re.match(r'^-?\s*\d+\s*-?$', line):
                return True
            if re.match(r'^第?\s*\d+\s*页$', line):
                return True
            return False

        # 策略1: 通用章节标题评分
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            if is_noise_line(stripped_line):
                continue

            score = 0
            # 行长度更像标题（短行）
            if 1 <= len(stripped_line) <= 20:
                score += 2
            elif len(stripped_line) <= 30:
                score += 1

            # 常见标题模式
            for pattern in chapter_patterns:
                if re.match(pattern, stripped_line):
                    score += 3
                    break

            # 章节关键词
            if re.search(r'(章|卷|篇|节|Chapter|CHAPTER|Part|PART)', stripped_line):
                score += 2

            # 前后空行（标题常独占行）
            prev_line = lines[i - 1].strip() if i > 0 else ""
            next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
            if not prev_line:
                score += 1
            if not next_line:
                score += 1

            if score >= 4:
                title = stripped_line
                if '第【' in title and '段：' in title:
                    parts = title.split('：', 1)
                    if len(parts) > 1:
                        title = parts[1].strip()
                chapter_positions.append({
                    'line_num': i,
                    'title': title,
                    'content_start': i + 1
                })
                stats["patterns_matched"] += 1

        # 策略2: 尝试匹配已知书籍的章节列表（通用辅助）
        for book_name, chapters_list in known_book_chapters.items():
            found_chapters = []
            normalized_targets = {normalize_title(t): t for t in chapters_list}

            for i, line in enumerate(lines):
                stripped = line.strip()
                if not stripped:
                    continue
                normalized_line = normalize_title(stripped)
                if normalized_line in normalized_targets:
                    found_chapters.append({
                        'line_num': i,
                        'title': normalized_targets[normalized_line],
                        'content_start': i + 1
                    })
                    continue

                # 处理“学而第一/为政第二”等样式：前缀匹配章节名
                for normalized_target, original_title in normalized_targets.items():
                    if normalized_line.startswith(normalized_target) and len(normalized_line) <= len(normalized_target) + 4:
                        found_chapters.append({
                            'line_num': i,
                            'title': original_title,
                            'content_start': i + 1
                        })
                        break

            # 如果找到至少一半章节，认为匹配成功
            threshold = max(3, len(chapters_list) // 2)
            if len(found_chapters) >= threshold:
                found_chapters.sort(key=lambda x: x['line_num'])
                chapter_positions = found_chapters
                stats["strategy"] = "known_book"
                stats["known_book_hit"] = book_name
                logger.info(f"✅ 识别为《{book_name}》格式，找到 {len(found_chapters)} 个章节")
                break

        # 如果没找到章节，按段落分割
        if not chapter_positions:
            logger.warning("⚠️  未检测到章节结构，按段落分割")
            stats["strategy"] = "fallback_paragraph"
            stats["fallback"] = True
            paragraphs = self.text_processor.split_text_by_paragraph(text)

            # 每10个段落合并为一章
            chunk_size = 10
            for i in range(0, len(paragraphs), chunk_size):
                chapter_text = '\n\n'.join(paragraphs[i:i + chunk_size])
                chapters.append(Chapter(
                    chapter_id=str(uuid.uuid4()),
                    chapter_number=len(chapters) + 1,
                    title=f"段落 {i // chunk_size + 1}",
                    content=chapter_text,
                    page_range=None
                ))
        else:
            # 智能合并：按标题分组（如多段属于同一卷则合并）
            logger.info(f"📚 检测到 {len(chapter_positions)} 个章节标记，开始智能合并...")

            # 提取主要的章节标题（如"第一卷"、"第二卷"）
            major_chapters = []
            current_content_lines = []
            current_major_title = None

            for i, pos in enumerate(chapter_positions):
                title = pos['title']
                start_line = pos['content_start']

                # 判断是否为主要章节标题
                is_major = (
                    '卷' in title or
                    '章' in title or
                    '篇' in title or
                    'Chapter' in title.lower() or
                    re.match(r'^第[一二三四五六七八九十百零]+、', title) or
                    re.match(r'^[\u4e00-\u9fff]{1,3}第[\u4e00-\u9fff一二三四五六七八九十百零\d]+', title) or  # "学而第一"
                    (re.search(r'第[一二三四五六七八九十百零\d]+$', title) and len(title) <= 5)  # "公冶长第五"
                )

                if is_major:
                    # 保存之前的章节
                    if current_major_title and current_content_lines:
                        chapter_text = '\n'.join(current_content_lines).strip()
                        if chapter_text:
                            chapters.append(Chapter(
                                chapter_id=str(uuid.uuid4()),
                                chapter_number=len(chapters) + 1,
                                title=current_major_title,
                                content=chapter_text,
                                page_range=None
                            ))

                    # 开始新章节
                    current_major_title = title
                    current_content_lines = []
                else:
                    # 不是主要标题，继续累积内容
                    pass

                # 确定内容范围
                if i < len(chapter_positions) - 1:
                    end_line = chapter_positions[i + 1]['line_num']
                else:
                    end_line = len(lines)

                # 累积内容行
                content_lines = lines[start_line:end_line]
                current_content_lines.extend(content_lines)

            # 保存最后一个章节
            if current_major_title and current_content_lines:
                chapter_text = '\n'.join(current_content_lines).strip()
                if chapter_text:
                    chapters.append(Chapter(
                        chapter_id=str(uuid.uuid4()),
                        chapter_number=len(chapters) + 1,
                        title=current_major_title,
                        content=chapter_text,
                        page_range=None
                    ))

            # 如果没有主要章节，则按原始分割
            if not chapters:
                logger.warning("⚠️  未检测到主要章节，使用原始分割")
                for i, pos in enumerate(chapter_positions):
                    start_line = pos['content_start']
                    if i < len(chapter_positions) - 1:
                        end_line = chapter_positions[i + 1]['line_num']
                    else:
                        end_line = len(lines)

                    chapter_lines = lines[start_line:end_line]
                    chapter_text = '\n'.join(chapter_lines).strip()

                    if chapter_text:
                        chapters.append(Chapter(
                            chapter_id=str(uuid.uuid4()),
                            chapter_number=len(chapters) + 1,
                            title=pos['title'],
                            content=chapter_text,
                            page_range=None
                        ))

        return chapters, stats

    async def _extract_core_viewpoints(
        self,
        chapters: List[Chapter],
        max_viewpoints_per_chapter: int = 5
    ) -> List[CoreViewpoint]:
        """
        提取核心观点

        策略：
        1. 对每个章节提取关键句
        2. 对关键句进行总结
        3. 提取关键词
        """
        core_viewpoints = []

        for chapter in chapters:
            # 提取关键句
            key_sentences = self.text_processor.extract_key_sentences(
                chapter.content,
                top_k=max_viewpoints_per_chapter
            )

            for sentence, score in key_sentences:
                # 提取关键词
                keywords = self.text_processor.extract_keywords(
                    sentence,
                    top_k=5,
                    with_weight=False
                )

                # 创建核心观点对象
                viewpoint = CoreViewpoint(
                    viewpoint_id=str(uuid.uuid4()),
                    content=sentence,
                    original_text=sentence,  # 这里可以精确定位到原文
                    chapter_id=chapter.chapter_id,
                    context=sentence[:100] + "..." if len(sentence) > 100 else sentence,
                    keywords=keywords
                )
                core_viewpoints.append(viewpoint)

        return core_viewpoints


# 全局单例
_document_parser: Optional[DocumentParser] = None


def get_document_parser() -> DocumentParser:
    """获取文档解析器单例"""
    global _document_parser
    if _document_parser is None:
        _document_parser = DocumentParser()
    return _document_parser


if __name__ == "__main__":
    # 测试代码
    import asyncio

    async def test():
        """测试文档解析"""
        parser = get_document_parser()

        # 测试文件路径（从backend目录出发）
        test_file = "../books/理想国.txt"

        try:
            book = await parser.parse_book(
                file_path=test_file,
                title="理想国",
                author="柏拉图"
            )

            print(f"✅ 解析成功!")
            print(f"标题: {book.title}")
            print(f"作者: {book.author}")
            print(f"总字数: {book.total_words}")
            print(f"章节数: {len(book.chapters)}")
            print(f"核心观点数: {len(book.core_viewpoints)}")

            print("\n章节列表:")
            for chapter in book.chapters[:5]:  # 只显示前5章
                print(f"  - {chapter.title}")

            print("\n核心观点示例:")
            for viewpoint in book.core_viewpoints[:3]:  # 只显示前3个
                print(f"  - {viewpoint.content[:50]}...")

        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()

    # 运行测试
    asyncio.run(test())
