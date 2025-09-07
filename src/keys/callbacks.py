from enum import StrEnum
from eiogram.utils.callback_data import CallbackData
from .enums import SectionType, ActionType, SubActionType


class BotCB(CallbackData, prefix="x"):
    section: SectionType = SectionType.HOME
    action: ActionType = ActionType.MENU
    sub_action: SubActionType | None = None
    approval: bool | None = None
    page: int | None = None
    target: int | str | StrEnum | None = None
