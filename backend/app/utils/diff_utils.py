"""
文本Diff工具
"""
from difflib import SequenceMatcher
from typing import List, Dict


def _build_opcodes(a: str, b: str) -> List[Dict]:
    matcher = SequenceMatcher(a=a, b=b)
    opcodes = matcher.get_opcodes()
    return [
        {
            "tag": tag,
            "a_start": a_start,
            "a_end": a_end,
            "b_start": b_start,
            "b_end": b_end
        }
        for tag, a_start, a_end, b_start, b_end in opcodes
    ]


def diff_text(a: str, b: str) -> Dict:
    """
    输出diff结构
    tag: equal/replace/delete/insert
    """
    return {
        "opcodes": _build_opcodes(a, b),
        "a_len": len(a),
        "b_len": len(b)
    }
