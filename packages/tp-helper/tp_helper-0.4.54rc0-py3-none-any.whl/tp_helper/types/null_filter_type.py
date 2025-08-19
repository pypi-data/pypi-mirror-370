from enum import Enum


class NullFilterType(Enum):
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"