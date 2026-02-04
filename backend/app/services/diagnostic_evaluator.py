"""
诊断评估服务
根据受众Persona对输出内容进行基础评估
"""
from typing import Dict, Any, Optional, List
from loguru import logger

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

        metrics["character_count"] = char_count
        metrics["sentence_count"] = sentence_count
        metrics["avg_sentence_length"] = avg_sentence_length

        if audience:
            constraints = self.adapter.build_constraints(audience)
            target_len = constraints["sentence_length"]["target_chars"]
            metrics["target_sentence_length"] = target_len
            metrics["sentence_length_gap"] = round(avg_sentence_length - target_len, 2)

            if avg_sentence_length > target_len + 6:
                issues.append("句长偏长，可能影响可读性")
            if avg_sentence_length < target_len - 6:
                issues.append("句长偏短，表达可能过于碎片化")

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


_evaluator: DiagnosticEvaluator | None = None


def get_diagnostic_evaluator() -> DiagnosticEvaluator:
    """获取诊断评估器单例"""
    global _evaluator
    if _evaluator is None:
        _evaluator = DiagnosticEvaluator()
    return _evaluator
