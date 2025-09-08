from eiogram import Router
from eiogram.types import CallbackQuery
from eiogram.filters import IgnoreStateFilter
from eiogram.state import StateManager

from src.keys import BotCB, BotKB, SectionType, ActionType
from src.db import AsyncSession, Subscription, UserMessage
from src.lang import DialogText


router = Router()


@router.callback_query(
    BotCB.filter(section=SectionType.SUBS, action=ActionType.MENU),
    IgnoreStateFilter(),
)
async def sub_menu_handler(
    callback_query: CallbackQuery,
    callback_data: BotCB,
    db: AsyncSession,
    state: StateManager,
):
    await state.clear_state(db=db)
    pagination = await Subscription.get_paginated(db, page=int(callback_data.page) if callback_data.page else 1)
    update = await callback_query.message.edit(
        text=DialogText.SUBS_MENU,
        reply_markup=BotKB.subscriptions_menu(pagination=pagination),
    )
    return await UserMessage.clear(update, keep_current=True)
