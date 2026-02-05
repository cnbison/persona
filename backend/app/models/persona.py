"""
作者Persona模型
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class ThinkingStyle(str, Enum):
    """思维方式枚举"""
    INDUCTIVE = "inductive"  # 归纳法
    DEDUCTIVE = "deductive"  # 演绎法
    DIALECTICAL = "dialectical"  # 辩证法
    ANALYTICAL = "analytical"  # 分析法
    INTUITIVE = "intuitive"  # 直觉法


class PersonalityDimension(BaseModel):
    """人格维度评分"""
    dimension_name: str = Field(..., description="维度名称")
    score: int = Field(..., ge=1, le=5, description="评分（1-5分）")
    description: str = Field(..., description="维度描述")


class AuthorPersona(BaseModel):
    """作者Persona模型 - 6大维度"""

    # 基础信息
    persona_id: str = Field(..., description="Persona ID")
    author_name: str = Field(..., description="作者姓名")
    book_id: str = Field(..., description="关联的著作ID")

    # 维度1：思维方式
    thinking_style: ThinkingStyle = Field(..., description="思维方式类型")
    logic_pattern: str = Field(..., description="思维逻辑模式描述")
    reasoning_framework: str = Field(..., description="论证框架")

    # 维度2：思想体系
    core_philosophy: str = Field(..., description="核心哲学观点")
    theoretical_framework: str = Field(..., description="理论框架")
    value_system: List[str] = Field(default_factory=list, description="价值体系列表")
    key_concepts: Dict[str, str] = Field(default_factory=dict, description="核心概念及其定义")

    # 维度3：叙事风格
    narrative_style: str = Field(..., description="叙事偏好（幽默/严肃/口语/书面）")
    language_rhythm: str = Field(..., description="语言节奏")
    sentence_structure: str = Field(..., description="句式结构特征")
    rhetorical_devices: List[str] = Field(default_factory=list, description="修辞手法")

    # 维度4：价值观
    value_orientation: str = Field(..., description="价值立场（保守/激进/个人主义/集体主义）")
    value_judgment_framework: str = Field(..., description="价值判断框架")
    core_positions: List[str] = Field(default_factory=list, description="核心立场")
    opposed_positions: List[str] = Field(default_factory=list, description="反对立场")

    # 维度5：语气
    tone: str = Field(..., description="语气特征（温和/激烈/谦逊/自信）")
    emotion_tendency: str = Field(..., description="情感倾向")
    expressiveness: str = Field(..., description="表达方式（直白/委婉/热情/冷淡）")

    # 维度6：性格特征
    personality_traits: List[str] = Field(default_factory=list, description="性格特质（如幽默/严肃/开放/保守）")
    communication_style: str = Field(..., description="沟通风格")
    attitude_toward_audience: str = Field(..., description="对受众的态度")

    # 观点边界（用于合规性校验）
    viewpoint_boundaries: Dict[str, List[str]] = Field(
        default_factory=dict,
        description={
            "core_positions": ["核心主张列表"],
            "opposed_positions": ["反对观点列表"],
            "unmentioned_areas": ["未表态领域列表"]
        }
    )

    # 证据链接（可选）
    evidence_links: List[str] = Field(default_factory=list, description="证据链接或引用")

    # 元数据
    created_at: datetime = Field(default_factory=datetime.now)
    version: str = "1.0"


class AudiencePersona(BaseModel):
    """受众Persona模型"""

    audience_id: str = Field(..., description="受众Persona ID")
    label: str = Field(..., description="受众名称（如：高中生-理科）")
    book_id: Optional[str] = Field(None, description="关联的著作ID（可选）")

    # 受众画像
    education_stage: str = Field(..., description="教育阶段（小学/初中/高中/大学/成人）")
    prior_knowledge: str = Field(..., description="先验知识水平（入门/基础/进阶/专家）")
    cognitive_preference: str = Field(..., description="认知偏好（故事/逻辑/案例等）")
    language_preference: str = Field(..., description="语言风格偏好（简洁/严谨/比喻型）")
    tone_preference: str = Field(..., description="语气偏好（亲切/严肃/鼓励）")

    # 表达控制参数（1-5）
    term_density: int = Field(3, ge=1, le=5, description="术语密度")
    sentence_length: int = Field(3, ge=1, le=5, description="句长复杂度")
    abstraction_level: int = Field(3, ge=1, le=5, description="抽象程度")
    example_complexity: int = Field(3, ge=1, le=5, description="案例复杂度")
    proof_depth: int = Field(3, ge=1, le=5, description="论证深度")

    constraints: List[str] = Field(default_factory=list, description="硬性限制")

    created_at: datetime = Field(default_factory=datetime.now)
    version: str = "1.0"


class SystemPrompt(BaseModel):
    """角色System Prompt"""
    prompt_id: str = Field(..., description="Prompt ID")
    persona_id: str = Field(..., description="关联的Persona ID")
    role_type: str = Field(..., description="角色类型：author/host")

    # Prompt内容
    system_instruction: str = Field(..., description="系统指令")
    role_definition: str = Field(..., description="角色定位")
    constraints: List[str] = Field(default_factory=list, description="约束条件")
    examples: Optional[List[str]] = Field(None, description="示例对话")

    # 版本控制
    version: str = "1.0"
    created_at: datetime = Field(default_factory=datetime.now)


class HostPersona(BaseModel):
    """主持人Persona模型"""
    persona_id: str = Field(..., description="Persona ID")

    # 核心定位
    role_positioning: str = Field(
        default="引导者+诠释者+桥梁者",
        description="角色定位"
    )

    # 特质
    traits: List[str] = Field(
        default=["专业严谨", "亲和易懂", "尊重作者", "代表现代受众"],
        description="主持人特质"
    )

    # 知识储备
    knowledge_base: List[str] = Field(
        default_factory=lambda: ["精通著作内容", "熟悉作者生平", "了解时代背景", "把握热点话题"],
        description="知识储备"
    )

    # 语言风格
    language_style: str = Field(
        default="简洁通俗，擅长转化学术表述为现代语境",
        description="语言风格"
    )

    # 功能
    functions: List[str] = Field(
        default_factory=lambda: [
            "引导话题方向",
            "把控对话节奏",
            "深化内容理解",
            "连接现实热点"
        ],
        description="核心功能"
    )

    # 发言配置
    speaking_ratio: int = Field(default=40, description="发言时长占比（%）")
