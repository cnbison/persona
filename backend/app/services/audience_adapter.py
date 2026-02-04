"""
受众Persona适配服务
生成表达约束与可读性目标
"""
from typing import Dict, Any
from loguru import logger

from app.models.persona import AudiencePersona


class AudienceAdapter:
    """受众Persona适配器"""

    LEVEL_LABELS = {
        1: "极低",
        2: "较低",
        3: "中等",
        4: "较高",
        5: "极高"
    }

    SENTENCE_TARGET = {1: 10, 2: 15, 3: 20, 4: 28, 5: 36}
    TERM_DENSITY_TARGET = {1: 0.02, 2: 0.05, 3: 0.08, 4: 0.12, 5: 0.18}

    ABSTRACTION_DESC = {
        1: "高度具象",
        2: "偏具象",
        3: "适度平衡",
        4: "偏抽象",
        5: "高度抽象"
    }

    PROOF_DESC = {
        1: "结论先行，最少推导",
        2: "轻度推导",
        3: "平衡结论与推导",
        4: "推导为主",
        5: "严格推导与边界"
    }

    EXAMPLE_DESC = {
        1: "日常生活类比",
        2: "简单案例",
        3: "中等复杂案例",
        4: "专业案例",
        5: "技术/学术案例"
    }

    def build_constraints(self, audience: AudiencePersona) -> Dict[str, Any]:
        """生成表达约束与目标"""
        constraints = {
            "education_stage": audience.education_stage,
            "prior_knowledge": audience.prior_knowledge,
            "cognitive_preference": audience.cognitive_preference,
            "language_preference": audience.language_preference,
            "tone_preference": audience.tone_preference,
            "term_density": {
                "level": audience.term_density,
                "label": self.LEVEL_LABELS.get(audience.term_density, "中等"),
                "target_ratio": self.TERM_DENSITY_TARGET.get(audience.term_density, 0.08)
            },
            "sentence_length": {
                "level": audience.sentence_length,
                "label": self.LEVEL_LABELS.get(audience.sentence_length, "中等"),
                "target_chars": self.SENTENCE_TARGET.get(audience.sentence_length, 20)
            },
            "abstraction_level": {
                "level": audience.abstraction_level,
                "label": self.ABSTRACTION_DESC.get(audience.abstraction_level, "适度平衡")
            },
            "example_complexity": {
                "level": audience.example_complexity,
                "label": self.EXAMPLE_DESC.get(audience.example_complexity, "中等复杂案例")
            },
            "proof_depth": {
                "level": audience.proof_depth,
                "label": self.PROOF_DESC.get(audience.proof_depth, "平衡结论与推导")
            },
            "constraints": audience.constraints
        }

        logger.info("✅ 生成受众Persona表达约束")
        return constraints


_adapter: AudienceAdapter | None = None


def get_audience_adapter() -> AudienceAdapter:
    """获取受众Persona适配器单例"""
    global _adapter
    if _adapter is None:
        _adapter = AudienceAdapter()
    return _adapter
