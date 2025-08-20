from enum import Enum


class Channel(str, Enum):
    """渠道枚举"""
    OPENAI = "openai"
    VERTEXAI = "vertexai"
    AI_STUDIO = "ai-studio"

    # 默认的
    NORMAL = "normal"
