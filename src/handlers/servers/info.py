from eiogram import Router
from eiogram.types import CallbackQuery
from eiogram.filters import IgnoreStateFilter
from eiogram.state import StateManager

from src.keys import BotCB, BotKB, SectionType, ActionType
from src.db import AsyncSession, Server, UserMessage
from src.lang import DialogText

router = Router()


@router.callback_query(
    BotCB.filter(section=SectionType.SERVERS, action=ActionType.INFO),
    IgnoreStateFilter(),
)
async def server_info_handler(
    callback_query: CallbackQuery,
    callback_data: BotCB,
    db: AsyncSession,
    state: StateManager,
):
    await state.clear_state(db=db)
    server = await Server.get_by_id(db, int(callback_data.target))
    if not server:
        return await callback_query.answer(
            DialogText.SERVERS_NOT_FOUND, show_alert=True
        )
    update = await callback_query.message.edit(
        text=DialogText.SERVERS_INFO.format(**server.format()),
        reply_markup=BotKB.servers_update(server),
    )
    return await UserMessage.clear(update, keep_current=True)
