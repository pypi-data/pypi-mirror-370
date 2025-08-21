from enum import Enum


class EntityType(Enum):
    INPUT = "input"
    PROCESSOR = "processor"
    OUTPUT = "output"
    CONDITION = "condition"
    SCHEME = "scheme"
    INIT = "init"
