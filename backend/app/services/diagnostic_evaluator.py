"""
诊断评估服务
根据受众Persona对输出内容进行基础评估
"""
from typing import Dict, Any, Optional, List
from loguru import logger
import re

from app.models.persona import AudiencePersona
from app.services.audience_adapter import AudienceAdapter


class DiagnosticEvaluator:
    """诊断评估器"""

    def __init__(self):
        self.adapter = AudienceAdapter()
        logger.info("✅ 诊断评估服务初始化成功")

    def evaluate(
        self,
        text: str,
        audience: Optional[AudiencePersona] = None,
        locked_facts: Optional[list[str]] = None
    ) -> Dict[str, Any]:
        """生成诊断指标与问题列表"""
        metrics: Dict[str, Any] = {}
        issues: List[str] = []

        cleaned = text.strip()
        char_count = len(cleaned)
        sentences = self._split_sentences(cleaned)
        sentence_count = max(len(sentences), 1)
        avg_sentence_length = round(char_count / sentence_count, 2)
        paragraph_count = max(len([p for p in cleaned.splitlines() if p.strip()]), 1)

        metrics["character_count"] = char_count
        metrics["sentence_count"] = sentence_count
        metrics["avg_sentence_length"] = avg_sentence_length
        metrics["paragraph_count"] = paragraph_count

        term_density = self._estimate_term_density(cleaned)
        metrics["term_density_estimate"] = term_density

        if audience:
            constraints = self.adapter.build_constraints(audience)
            target_len = constraints["sentence_length"]["target_chars"]
            metrics["target_sentence_length"] = target_len
            metrics["sentence_length_gap"] = round(avg_sentence_length - target_len, 2)
            target_term = constraints["term_density"]["target_ratio"]
            metrics["target_term_density"] = target_term
            metrics["term_density_gap"] = round(term_density - target_term, 4)

            if avg_sentence_length > target_len + 6:
                issues.append("句长偏长，可能影响可读性")
            if avg_sentence_length < target_len - 6:
                issues.append("句长偏短，表达可能过于碎片化")
            if term_density > target_term + 0.05:
                issues.append("术语密度偏高，可能超出受众理解范围")
            if term_density < target_term - 0.05:
                issues.append("术语密度偏低，表达可能过于浅化")

            # 简单适配评分
            gap = abs(avg_sentence_length - target_len)
            metrics["audience_fit_score"] = max(0.0, round(1 - (gap / max(target_len, 1)), 2))

        missing_locked = []
        for item in locked_facts or []:
            if item and item not in cleaned:
                missing_locked.append(item)

        if missing_locked:
            issues.append("锁定概念/事实未完整保留")
            metrics["locked_facts_missing"] = len(missing_locked)
            metrics["locked_facts_total"] = len(locked_facts or [])
            if locked_facts:
                metrics["locked_facts_missing_ratio"] = round(len(missing_locked) / max(len(locked_facts), 1), 2)

        if char_count < 200:
            issues.append("内容偏短，信息量可能不足")

        logger.info("✅ 诊断评估完成")
        return {
            "metrics": metrics,
            "issues": issues
        }

    def _split_sentences(self, text: str) -> List[str]:
        parts = []
        buff = ""
        for ch in text:
            buff += ch
            if ch in "。！？!?\n":
                if buff.strip():
                    parts.append(buff.strip())
                buff = ""
        if buff.strip():
            parts.append(buff.strip())
        return parts

    def _estimate_term_density(self, text: str) -> float:
        word_like = re.findall(r"[A-Za-z]+|\\d+|[\\u4e00-\\u9fff]+", text)
        if not word_like:
            return 0.0

        term_candidates = re.findall(r"[A-Za-z]{3,}|\\d+|[\\u4e00-\\u9fff]{4,}", text)
        return round(len(term_candidates) / max(len(word_like), 1), 4)


_evaluator: DiagnosticEvaluator | None = None


def get_diagnostic_evaluator() -> DiagnosticEvaluator:
    """获取诊断评估器单例"""
    global _evaluator
    if _evaluator is None:
        _evaluator = DiagnosticEvaluator()
    return _evaluator
