"""
证据链接生成服务
"""
from typing import List
from sqlalchemy.orm import Session
from loguru import logger

from app.models.orm import AuthorPersonaORM, CoreViewpointORM, ChapterORM


class EvidenceLinker:
    """证据链接生成器"""

    def build_links(self, db: Session, persona: AuthorPersonaORM, limit: int = 8) -> List[str]:
        """生成证据链接（基于核心观点与章节）"""
        if not persona.book_id:
            return []

        viewpoints = (
            db.query(CoreViewpointORM)
            .filter(CoreViewpointORM.book_id == persona.book_id)
            .limit(limit)
            .all()
        )

        links: List[str] = []
        for vp in viewpoints:
            chapter = db.query(ChapterORM).filter(ChapterORM.chapter_id == vp.chapter_id).first()
            chapter_title = chapter.title if chapter else "未知章节"
            snippet = vp.original_text or vp.content
            snippet = snippet[:60] + "..." if snippet and len(snippet) > 60 else snippet

            links.append(f"{chapter_title}: {snippet}")

        logger.info(f"✅ 生成证据链接: {len(links)} 条")
        return links


def get_evidence_linker() -> EvidenceLinker:
    return EvidenceLinker()
