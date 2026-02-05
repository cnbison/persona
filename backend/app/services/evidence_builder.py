"""
证据库构建服务
"""
from typing import List
from sqlalchemy.orm import Session
from loguru import logger
import uuid

from app.models.orm import ChapterORM, ParagraphORM, EvidenceORM, CoreViewpointORM
from app.utils.text_processor import get_text_processor


class EvidenceBuilder:
    """证据库构建器"""

    def __init__(self):
        self.text_processor = get_text_processor()

    def build_paragraphs(self, db: Session, chapter: ChapterORM) -> List[ParagraphORM]:
        paragraphs = self.text_processor.split_text_by_paragraph(chapter.content or "")
        result: List[ParagraphORM] = []
        for idx, content in enumerate(paragraphs, start=1):
            paragraph = ParagraphORM(
                paragraph_id=uuid.uuid4().hex,
                book_id=chapter.book_id,
                chapter_id=chapter.chapter_id,
                paragraph_number=idx,
                content=content,
                word_count=len(content)
            )
            result.append(paragraph)
        return result

    def build_evidences(self, db: Session, chapter: ChapterORM, viewpoints: List[CoreViewpointORM], paragraphs: List[ParagraphORM]) -> List[EvidenceORM]:
        evidences: List[EvidenceORM] = []
        para_texts = [p.content for p in paragraphs]

        for viewpoint in viewpoints:
            snippet = viewpoint.original_text or viewpoint.content
            if not snippet:
                continue

            match_index = -1
            for idx, para in enumerate(para_texts):
                if snippet[:15] in para:
                    match_index = idx
                    break

            paragraph_id = paragraphs[match_index].paragraph_id if match_index >= 0 else None
            context_before = paragraphs[match_index - 1].content if match_index > 0 else None
            context_after = paragraphs[match_index + 1].content if match_index >= 0 and match_index + 1 < len(paragraphs) else None

            evidence_text = snippet
            evidence = EvidenceORM(
                evidence_id=uuid.uuid4().hex,
                book_id=chapter.book_id,
                chapter_id=chapter.chapter_id,
                paragraph_id=paragraph_id,
                viewpoint_id=viewpoint.viewpoint_id,
                evidence_text=evidence_text,
                context_before=context_before,
                context_after=context_after,
                keywords=viewpoint.keywords or [],
                score=1.0
            )
            evidences.append(evidence)

        return evidences

    def build_for_book(self, db: Session, book_id: str):
        chapters = db.query(ChapterORM).filter(ChapterORM.book_id == book_id).all()
        if not chapters:
            logger.warning("⚠️ 未找到章节，无法构建证据库")
            return

        for chapter in chapters:
            paragraphs = self.build_paragraphs(db, chapter)
            chapter.paragraph_count = len(paragraphs)
            for p in paragraphs:
                db.add(p)

            viewpoints = (
                db.query(CoreViewpointORM)
                .filter(CoreViewpointORM.chapter_id == chapter.chapter_id)
                .all()
            )
            evidences = self.build_evidences(db, chapter, viewpoints, paragraphs)
            for e in evidences:
                db.add(e)

        db.commit()
        logger.info(f"✅ 证据库构建完成: {book_id}")


def get_evidence_builder() -> EvidenceBuilder:
    return EvidenceBuilder()
