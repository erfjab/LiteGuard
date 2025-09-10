from eiogram import Router
from eiogram.types import CallbackQuery
from eiogram.filters import IgnoreStateFilter
from eiogram.state import StateManager

from src.keys import BotCB, BotKB, SectionType, ActionType
from src.db import AsyncSession, Setting, UserMessage
from src.lang import DialogText


router = Router()


@router.callback_query(
    BotCB.filter(section=SectionType.SETTINGS, action=ActionType.MENU),
    IgnoreStateFilter(),
)
async def settings_menu_handler(
    callback_query: CallbackQuery,
    db: AsyncSession,
    state: StateManager,
    setting: Setting,
):
    await state.clear_state(db=db)
    update = await callback_query.message.edit(
        text=DialogText.SETTINGS_MENU.format(**setting.format()),
        reply_markup=BotKB.settings_menu(setting=setting),
    )
    return await UserMessage.clear(update, keep_current=True)
