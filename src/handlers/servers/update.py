from eiogram import Router
from eiogram.types import CallbackQuery, Message
from eiogram.state import State, StateGroup, StateManager
from eiogram.filters import Text, StateFilter

from src.db import Server, AsyncSession, UserMessage
from src.keys import BotKB, BotCB, SectionType, ActionType, SubActionType
from src.lang import DialogText
from src.xui import XUIRequest

router = Router()


class ServerUpdateForm(StateGroup):
    input = State()
    approval = State()


@router.callback_query(BotCB.filter(section=SectionType.SERVERS, action=ActionType.UPDATE))
async def server_update_handler(
    callback_query: CallbackQuery,
    callback_data: BotCB,
    db: AsyncSession,
    state: StateManager,
):
    server = await Server.get_by_id(db, int(callback_data.target))
    if not server:
        return await callback_query.answer(DialogText.SERVERS_NOT_FOUND, show_alert=True)
    kb = BotKB.servers_back(server.id)
    match callback_data.sub_action:
        case SubActionType.REMARK:
            text = DialogText.SERVERS_ENTER_REMARK
            _state = ServerUpdateForm.input
        case SubActionType.CHANGE_CONFIG:
            text = DialogText.SERVERS_ENTER_CONFIG
            _state = ServerUpdateForm.input
        case SubActionType.REMOVE:
            return await callback_query.answer(text=DialogText.ACTIONS_NOT_ALLOW, show_alert=True)
        case SubActionType.ENABLED_STATUS:
            text = DialogText.ACTIONS_APPROVAL
            kb = BotKB.approval(section=SectionType.SERVERS, action=ActionType.UPDATE, target=server.id)
            _state = ServerUpdateForm.approval
    await state.upsert_context(db=db, state=_state, server_id=server.id, sub_action=callback_data.sub_action)
    return await callback_query.message.edit(text=text, reply_markup=kb)


@router.message(StateFilter(ServerUpdateForm.input), Text())
async def input_handler(message: Message, db: AsyncSession, state_data: dict, state: StateManager):
    server = await Server.get_by_id(db, int(state_data["server_id"]))
    if not server:
        update = await message.answer(DialogText.SERVERS_NOT_FOUND, reply_markup=BotKB.servers_back())
        await state.clear_state(db=db)
        return await UserMessage.clear(update)

    kb = BotKB.servers_back(target=server.id)
    match state_data["sub_action"]:
        case SubActionType.REMARK:
            if await Server.get_by_remark(db, message.text):
                update = await message.answer(
                    text=DialogText.SERVERS_REMARK_EXISTS,
                )
                return await UserMessage.add(update)
            await Server.update(db, server=server, remark=message.text)
        case SubActionType.CHANGE_CONFIG:
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
            await Server.upsert_access(db, server_id=server.id, access=dict(access.cookies))
            await Server.update(
                db,
                server=server,
                config={
                    "username": messages[0],
                    "password": messages[1],
                    "host": messages[2].strip("/"),
                    "sub": messages[3].strip("/"),
                },
            )

    await state.clear_state(db=db)
    update = await message.answer(text=DialogText.ACTIONS_SUCCESS, reply_markup=kb)
    return await UserMessage.clear(update)


@router.callback_query(
    BotCB.filter(section=SectionType.SERVERS, action=ActionType.UPDATE),
    StateFilter(ServerUpdateForm.approval),
)
async def approval_handler(
    callback_query: CallbackQuery,
    callback_data: BotCB,
    db: AsyncSession,
    state_data: dict,
    state: StateManager,
):
    await state.clear_state(db=db)
    server = await Server.get_by_id(db, int(state_data["server_id"]))
    if not server:
        update = await callback_query.message.answer(DialogText.SERVERS_NOT_FOUND, reply_markup=BotKB.servers_back())
        return await UserMessage.clear(update)

    kb = BotKB.servers_back(server.id)

    if not callback_data.approval:
        return await callback_query.message.edit(text=DialogText.ACTIONS_FORGET, reply_markup=kb)

    match state_data["sub_action"]:
        case SubActionType.ENABLED_STATUS:
            await Server.update(db, server=server, enabled=not server.enabled)
        case SubActionType.REMOVE:
            kb = BotKB.servers_back()
            await Server.remove(db, server=server)

    return await callback_query.message.edit(text=DialogText.ACTIONS_SUCCESS, reply_markup=kb)
