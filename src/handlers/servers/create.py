from eiogram import Router
from eiogram.types import CallbackQuery, Message
from eiogram.filters import StateFilter, Text
from eiogram.state import StateManager, State, StateGroup

from src.keys import BotCB, BotKB, SectionType, ActionType
from src.db import AsyncSession, Server, UserMessage
from src.lang import DialogText
from src.xui import XUIRequest

router = Router()


class ServerCreateForm(StateGroup):
    remark = State()
    config = State()


@router.callback_query(
    BotCB.filter(section=SectionType.SERVERS, action=ActionType.CREATE),
)
async def server_create_handler(callback_query: CallbackQuery, db: AsyncSession, state: StateManager):
    await state.set_state(db=db, state=ServerCreateForm.remark)
    return await callback_query.message.edit(text=DialogText.SERVERS_ENTER_REMARK, reply_markup=BotKB.servers_back())


@router.message(StateFilter(ServerCreateForm.remark), Text())
async def server_remark_handler(message: Message, db: AsyncSession, state: StateManager):
    if await Server.get_by_remark(db, message.text):
        update = await message.answer(
            text=DialogText.SERVERS_REMARK_EXISTS,
        )
        return await UserMessage.add(update)
    await state.upsert_context(db=db, state=ServerCreateForm.config, remark=message.text)
    update = await message.answer(text=DialogText.SERVERS_ENTER_CONFIG, reply_markup=BotKB.servers_back())
    return await UserMessage.clear(update)


@router.message(StateFilter(ServerCreateForm.config), Text())
async def server_config_handler(message: Message, db: AsyncSession, state: StateManager, state_data: dict):
    messages = message.text.split()
    if len(messages) != 4:
        update = await message.answer(
            text=DialogText.SERVERS_INVALID_CONFIG_FORMAT,
        )
        return await UserMessage.add(update)

    access = await XUIRequest.login(host=messages[2].strip("/"), username=messages[0], password=messages[1])
    if not access:
        update = await message.answer(
            text=DialogText.SERVERS_INVALID_ACCESS,
        )
        return await UserMessage.add(update)

    server = await Server.create(
        db,
        remark=state_data["remark"],
        config={
            "host": messages[2].strip("/"),
            "username": messages[0],
            "password": messages[1],
            "sub": messages[3].strip("/"),
        },
    )
    await Server.upsert_access(db, server_id=server.id, access=dict(access.cookies))
    await state.clear_state(db=db)
    update = await message.answer(text=DialogText.ACTIONS_SUCCESS, reply_markup=BotKB.servers_back(server.id))
    return await UserMessage.clear(update)
