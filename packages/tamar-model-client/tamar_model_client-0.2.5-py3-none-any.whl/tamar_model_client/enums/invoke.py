from enum import Enum


class InvokeType(str, Enum):
    """模型调用类型枚举"""
    RESPONSES = "responses"
    CHAT_COMPLETIONS = "chat-completions"

    GENERATION = "generation"  # 生成类，默认的值
    IMAGE_GENERATION = "image-generation"
    IMAGE_EDIT_GENERATION = "image-edit-generation"
    IMAGE_GENERATION_GENAI = "image-generation-genai"  # GenAI SDK图像生成
