from eiogram import Router
from eiogram.types import CallbackQuery
from eiogram.filters import IgnoreStateFilter
from eiogram.state import StateManager

from src.keys import BotCB, BotKB, SectionType, ActionType
from src.db import AsyncSession, Subscription, UserMessage
from src.lang import DialogText

router = Router()


@router.callback_query(
    BotCB.filter(section=SectionType.SUBS, action=ActionType.INFO),
    IgnoreStateFilter(),
)
async def sub_info_handler(
    callback_query: CallbackQuery,
    callback_data: BotCB,
    db: AsyncSession,
    state: StateManager,
):
    await state.clear_state(db=db)
    sub = await Subscription.get_by_id(db, int(callback_data.target))
    if not sub:
        return await callback_query.answer(DialogText.SUBS_NOT_FOUND, show_alert=True)
    update = await callback_query.message.edit(
        text=DialogText.SUBS_INFO.format(**sub.format()),
        reply_markup=BotKB.subs_update(sub),
    )
    return await UserMessage.clear(update, keep_current=True)
