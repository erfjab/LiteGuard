from enum import StrEnum


class SectionType(StrEnum):
    HOME = "hm"
    SERVERS = "sv"
    STATS = "st"
    USERS = "us"
    SUBS = "sb"
    SETTING = "stg"
    API_KEYS = "ak"
    TEST = "tt"
    ISSUE = "is"


class ActionType(StrEnum):
    MENU = "mn"
    INFO = "nf"
    CREATE = "cr"
    UPDATE = "up"
    LIST = "ls"


class SubActionType(StrEnum):
    REMARK = "rm"
    CHANGE_CONFIG = "cc"
    ENABLED_STATUS = "es"
    REMOVE = "rv"
    EXPIRE = "ex"
    USAGE_LIMIT = "ul"
    RESET_USAGE = "ru"
    REVOKE = "rk"
    QRCODE = "qc"
