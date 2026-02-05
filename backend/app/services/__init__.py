"""服务层模块"""
from app.services.document_parser import get_document_parser
from app.services.persona_builder import get_persona_builder
from app.services.outline_generator import get_outline_generator
from app.services.dialogue_generator import get_dialogue_generator
from app.services.audience_adapter import get_audience_adapter
from app.services.output_generator import get_output_generator
from app.services.diagnostic_evaluator import get_diagnostic_evaluator
from app.services.evidence_linker import get_evidence_linker
from app.services.evidence_builder import get_evidence_builder

__all__ = [
    "get_document_parser",
    "get_persona_builder",
    "get_outline_generator",
    "get_dialogue_generator",
    "get_audience_adapter",
    "get_output_generator",
    "get_diagnostic_evaluator",
    "get_evidence_linker",
    "get_evidence_builder"
]
