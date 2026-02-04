"""
文件处理工具
提供文件上传、类型验证、大小限制等功能
"""
import os
import hashlib
import mimetypes
from pathlib import Path
from typing import Optional, List
from loguru import logger
from datetime import datetime

from app.utils.config import settings


class FileHandler:
    """
    文件处理工具类

    功能：
    - 文件上传处理
    - 文件类型验证
    - 文件大小限制
    - 文件哈希计算
    - 安全文件名生成
    """

    # 允许的文件类型
    ALLOWED_EXTENSIONS = {
        'pdf', 'epub', 'txt', 'docx', 'mobi'
    }

    # 文件类型MIME映射
    MIME_TYPES = {
        'application/pdf': 'pdf',
        'application/epub+zip': 'epub',
        'text/plain': 'txt',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
        'application/x-mobipocket-ebook': 'mobi'
    }

    # 最大文件大小（默认50MB）
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

    def __init__(self):
        """初始化文件处理器"""
        # 确保上传目录存在
        self.upload_dir = Path(settings.books_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ 文件上传目录: {self.upload_dir}")

    def validate_file_type(self, filename: str, mime_type: Optional[str] = None) -> bool:
        """
        验证文件类型

        参数:
            filename: 文件名
            mime_type: MIME类型（可选）

        返回:
            是否为允许的类型
        """
        # 从文件名提取扩展名
        ext = self.get_file_extension(filename)

        if ext not in self.ALLOWED_EXTENSIONS:
            logger.warning(f"❌ 不允许的文件类型: {ext}")
            return False

        # 如果提供了MIME类型，也进行验证
        if mime_type:
            expected_ext = self.MIME_TYPES.get(mime_type)
            if expected_ext and expected_ext != ext:
                logger.warning(f"❌ MIME类型与扩展名不匹配: {mime_type} vs {ext}")
                return False

        return True

    def validate_file_size(self, file_size: int) -> bool:
        """
        验证文件大小

        参数:
            file_size: 文件大小（字节）

        返回:
            是否在允许的大小范围内
        """
        if file_size > self.MAX_FILE_SIZE:
            logger.warning(f"❌ 文件过大: {file_size / 1024 / 1024:.2f}MB (最大: {self.MAX_FILE_SIZE / 1024 / 1024}MB)")
            return False

        if file_size == 0:
            logger.warning("❌ 文件为空")
            return False

        return True

    def get_file_extension(self, filename: str) -> str:
        """
        获取文件扩展名（小写）

        参数:
            filename: 文件名

        返回:
            扩展名（如'pdf', 'epub'）
        """
        return Path(filename).suffix.lower().lstrip('.')

    def generate_safe_filename(self, filename: str) -> str:
        """
        生成安全的文件名

        移除特殊字符，保留中文、英文、数字、下划线、连字符

        参数:
            filename: 原始文件名

        返回:
            安全的文件名
        """
        # 提取文件名和扩展名
        path = Path(filename)
        name = path.stem
        ext = path.suffix

        # 移除特殊字符
        # 保留中文、英文、数字、下划线、连字符、空格
        safe_name = re.sub(r'[^\w\u4e00-\u9fff\s-]', '', name)

        # 替换空格为下划线
        safe_name = safe_name.replace(' ', '_')

        # 移除连续的特殊字符
        safe_name = re.sub(r'[_\-]{2,}', '_', safe_name)

        # 添加时间戳避免重名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = f"{safe_name}_{timestamp}{ext}"

        return safe_name

    def calculate_file_hash(self, file_path: str, algorithm: str = 'md5') -> str:
        """
        计算文件哈希值

        参数:
            file_path: 文件路径
            algorithm: 哈希算法（md5, sha1, sha256）

        返回:
            十六进制哈希值
        """
        hash_func = hashlib.new(algorithm)

        with open(file_path, 'rb') as f:
            # 分块读取文件（避免大文件内存问题）
            for chunk in iter(lambda: f.read(8192), b''):
                hash_func.update(chunk)

        return hash_func.hexdigest()

    def save_uploaded_file(
        self,
        file_content: bytes,
        original_filename: str,
        mime_type: Optional[str] = None
    ) -> dict:
        """
        保存上传的文件

        参数:
            file_content: 文件内容（字节）
            original_filename: 原始文件名
            mime_type: MIME类型（可选）

        返回:
            {
                "success": True/False,
                "file_path": "保存的文件路径",
                "filename": "保存的文件名",
                "size": 文件大小,
                "hash": "文件哈希值",
                "error": "错误信息（如果失败）"
            }
        """
        try:
            # 验证文件大小
            file_size = len(file_content)
            if not self.validate_file_size(file_size):
                return {
                    "success": False,
                    "error": "文件大小超出限制"
                }

            # 验证文件类型
            if not self.validate_file_type(original_filename, mime_type):
                return {
                    "success": False,
                    "error": "不支持的文件类型"
                }

            # 生成安全文件名
            safe_filename = self.generate_safe_filename(original_filename)
            file_path = self.upload_dir / safe_filename

            # 保存文件
            with open(file_path, 'wb') as f:
                f.write(file_content)

            # 计算哈希值
            file_hash = self.calculate_file_hash(str(file_path))

            logger.info(f"✅ 文件保存成功: {safe_filename} ({file_size / 1024:.2f}KB)")

            return {
                "success": True,
                "file_path": str(file_path),
                "filename": safe_filename,
                "original_filename": original_filename,
                "size": file_size,
                "hash": file_hash
            }

        except Exception as e:
            logger.error(f"❌ 文件保存失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def delete_file(self, file_path: str) -> bool:
        """
        删除文件

        参数:
            file_path: 文件路径

        返回:
            是否删除成功
        """
        try:
            path = Path(file_path)

            # 安全检查：确保文件在上传目录内
            if not str(path).startswith(str(self.upload_dir)):
                logger.warning(f"❌ 尝试删除上传目录外的文件: {file_path}")
                return False

            if path.exists():
                path.unlink()
                logger.info(f"✅ 文件删除成功: {file_path}")
                return True
            else:
                logger.warning(f"⚠️  文件不存在: {file_path}")
                return False

        except Exception as e:
            logger.error(f"❌ 文件删除失败: {e}")
            return False

    def list_files(self, pattern: str = "*") -> List[dict]:
        """
        列出上传目录的文件

        参数:
            pattern: 文件匹配模式（如'*.pdf'）

        返回:
            [
                {
                    "filename": "文件名",
                    "path": "完整路径",
                    "size": 文件大小,
                    "modified_time": "修改时间"
                },
                ...
            ]
        """
        try:
            files = []
            for file_path in self.upload_dir.glob(pattern):
                if file_path.is_file():
                    stat = file_path.stat()
                    files.append({
                        "filename": file_path.name,
                        "path": str(file_path),
                        "size": stat.st_size,
                        "modified_time": datetime.fromtimestamp(stat.st_mtime)
                    })

            # 按修改时间倒序排序
            files.sort(key=lambda x: x["modified_time"], reverse=True)

            return files

        except Exception as e:
            logger.error(f"❌ 列出文件失败: {e}")
            return []

    def get_file_info(self, file_path: str) -> Optional[dict]:
        """
        获取文件信息

        参数:
            file_path: 文件路径

        返回:
            文件信息字典
        """
        try:
            path = Path(file_path)

            if not path.exists():
                return None

            stat = path.stat()
            return {
                "filename": path.name,
                "extension": self.get_file_extension(path.name),
                "path": str(path),
                "size": stat.st_size,
                "created_time": datetime.fromtimestamp(stat.st_ctime),
                "modified_time": datetime.fromtimestamp(stat.st_mtime),
                "hash": self.calculate_file_hash(file_path)
            }

        except Exception as e:
            logger.error(f"❌ 获取文件信息失败: {e}")
            return None


import re  # 需要导入re模块用于generate_safe_filename


# 全局单例
_file_handler: Optional[FileHandler] = None


def get_file_handler() -> FileHandler:
    """获取文件处理器单例"""
    global _file_handler
    if _file_handler is None:
        _file_handler = FileHandler()
    return _file_handler


if __name__ == "__main__":
    # 测试代码
    handler = get_file_handler()

    print("=" * 50)
    print("测试文件类型验证")
    print("=" * 50)

    test_files = [
        "test.pdf",
        "test.epub",
        "test.txt",
        "test.exe",
        "test.doc"
    ]

    for filename in test_files:
        is_valid = handler.validate_file_type(filename)
        print(f"{filename}: {'✅ 允许' if is_valid else '❌ 不允许'}")

    print("\n" + "=" * 50)
    print("测试安全文件名生成")
    print("=" * 50)

    test_filenames = [
        "测试文件.pdf",
        "Test File (2023).txt",
        "test@#$%file.epub"
    ]

    for filename in test_filenames:
        safe_name = handler.generate_safe_filename(filename)
        print(f"{filename} -> {safe_name}")

    print("\n" + "=" * 50)
    print("测试列出文件")
    print("=" * 50)

    files = handler.list_files()
    print(f"找到 {len(files)} 个文件")
    for file_info in files[:5]:  # 只显示前5个
        print(f"- {file_info['filename']} ({file_info['size'] / 1024:.2f}KB)")
