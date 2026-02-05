"""
Persona卡片生成服务
用于基于已有Persona字段生成可展示的摘要卡片
"""
from typing import Dict, Any, List

from app.models.orm import AuthorPersonaORM


def _safe_join(items: List[str], limit: int = 4) -> str:
    if not items:
        return ""
    return "、".join(items[:limit])


def build_persona_card(persona: AuthorPersonaORM) -> Dict[str, Any]:
    """根据Persona字段生成卡片摘要"""
    one_liner = persona.core_philosophy or persona.theoretical_framework or "暂无核心哲学摘要"
    if len(one_liner) > 120:
        one_liner = one_liner[:120] + "..."

    style_bits = []
    if persona.thinking_style:
        style_bits.append(f"思维方式：{persona.thinking_style}")
    if persona.narrative_style:
        style_bits.append(f"叙事：{persona.narrative_style}")
    if persona.tone:
        style_bits.append(f"语气：{persona.tone}")
    style_summary = " · ".join(style_bits) if style_bits else "暂无风格摘要"

    if persona.opposed_positions:
        boundary_tip = f"避免主张：{_safe_join(persona.opposed_positions, 4)}"
    else:
        boundary_tip = "暂无明确边界提示"

    return {
        "persona_id": persona.persona_id,
        "author_name": persona.author_name or "",
        "version": persona.version or "1.0",
        "one_liner": one_liner,
        "style_summary": style_summary,
        "boundary_tip": boundary_tip,
        "core_positions": persona.core_positions or [],
        "key_concepts": list((persona.key_concepts or {}).keys()),
        "evidence_links": persona.evidence_links or []
    }
