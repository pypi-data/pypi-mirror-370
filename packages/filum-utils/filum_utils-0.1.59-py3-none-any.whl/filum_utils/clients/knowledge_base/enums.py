from enum import Enum


class KBDocumentStatusEnum(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"


class KBDocumentColumnDataTypeEnum(str, Enum):
    TEXT = "text"
    NUMBER = "number"
    BOOLEAN = "boolean"
    GEOLOCATION = "geolocation"
    IMAGE = "image"
    DATE = "date"
    ARRAY = "array"
    OBJECT = "object"


class KBDocumentColumnFilterTypeEnum(str, Enum):
    ENUM = "enum"
    RANGE = "range"
    TEXT = "text"
