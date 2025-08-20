from enum import Enum


class ModelProvider(Enum):
    BERRYDB_MODEL = "berrydb"
    VERTEX_AI_MODEL = "vertexai"
    HUGGING_FACE_MODEL = "huggingface"
    CUSTOM_MODEL = "custom"