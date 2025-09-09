from eiogram import Router
from eiogram.types import CallbackQuery, Message
from eiogram.state import State, StateGroup, StateManager
from eiogram.filters import Text, StateFilter

from src.db import Server, AsyncSession, UserMessage, Subscription
from src.keys import BotKB, BotCB, SectionType, ActionType, SubActionType
from src.lang import DialogText
from src.xui import XUIManager
from src.utils.qrcode import create_qr

router = Router()


class SubUpdateForm(StateGroup):
    input = State()
    approval = State()


@router.callback_query(BotCB.filter(section=SectionType.SUBS, action=ActionType.UPDATE))
async def sub_update_handler(
    callback_query: CallbackQuery,
    callback_data: BotCB,
    db: AsyncSession,
    state: StateManager,
):
    sub = await Subscription.get_by_id(db, int(callback_data.target))
    if not sub:
        return await callback_query.answer(DialogText.SUBS_NOT_FOUND, show_alert=True)
    kb = BotKB.subs_back(sub.id)
    _state = SubUpdateForm.input
    match callback_data.sub_action:
        case SubActionType.QRCODE:
            text = DialogText.SUBS_QRCODE.format(**sub.format())
            update = await callback_query.message.answer_photo(photo=create_qr(sub.link), caption=text)
            return await UserMessage.add(update)
        case SubActionType.REMARK:
            text = DialogText.SUBS_ENTER_REMARK
        case SubActionType.EXPIRE:
            text = DialogText.SUBS_ENTER_EXPIRE
        case SubActionType.USAGE_LIMIT:
            text = DialogText.SUBS_ENTER_LIMIT_USAGE
        case SubActionType.ENABLED_STATUS | SubActionType.REMOVE | SubActionType.REVOKE | SubActionType.RESET_USAGE:
            text = DialogText.ACTIONS_APPROVAL
            kb = BotKB.approval(section=SectionType.SUBS, action=ActionType.UPDATE, target=sub.id)
            _state = SubUpdateForm.approval
    await state.upsert_context(db=db, state=_state, sub_id=sub.id, sub_action=callback_data.sub_action)
    return await callback_query.message.edit(text=text, reply_markup=kb)


@router.message(StateFilter(SubUpdateForm.input), Text())
async def input_handler(message: Message, db: AsyncSession, state_data: dict, state: StateManager):
    sub = await Subscription.get_by_id(db, int(state_data["sub_id"]))
    if not sub:
        update = await message.answer(DialogText.SUBS_NOT_FOUND, reply_markup=BotKB.subs_back())
        await state.clear_state(db=db)
        return await UserMessage.clear(update)

    kb = BotKB.subs_back(target=sub.id)
    match state_data["sub_action"]:
        case SubActionType.REMARK:
            if await Subscription.get_by_remark(db, message.text):
                update = await message.answer(
                    text=DialogText.SUBS_REMARK_EXISTS,
                )
                return await UserMessage.add(update)
            await Subscription.update(db, sub=sub, remark=message.text)
        case SubActionType.EXPIRE:
            if not message.text[:-1].isdigit() or message.text[-1] not in ["d", "h"] or int(message.text[:-1]) <= 0:
                update = await message.answer(
                    text=DialogText.SUBS_INVALID_EXPIRE,
                )
                return await UserMessage.add(update)

            expire = int(message.text[:-1]) * (24 * 3600 if message.text[-1] == "d" else 3600)
            await state.upsert_context(
                db=db,
                state=SubUpdateForm.approval,
                expire=expire,
            )
            update = await message.answer(
                text=DialogText.SUBS_ASK_START_AFTER_FIRST_USE,
                reply_markup=BotKB.approval(section=SectionType.SUBS, action=ActionType.UPDATE, target=sub.id),
            )
            return await UserMessage.clear(update)

        case SubActionType.USAGE_LIMIT:
            if not message.text.isdigit() or int(message.text) <= 0:
                update = await message.answer(
                    text=DialogText.SUBS_INVALID_LIMIT_USAGE,
                )
                return await UserMessage.add(update)
            limit_usage = int(message.text) * 1024 * 1024 * 1024
            await Subscription.update(db, sub=sub, limit_usage=limit_usage)

    await state.clear_state(db=db)
    update = await message.answer(text=DialogText.ACTIONS_SUCCESS, reply_markup=kb)
    return await UserMessage.clear(update)


@router.callback_query(
    BotCB.filter(section=SectionType.SUBS, action=ActionType.UPDATE),
    StateFilter(SubUpdateForm.approval),
)
async def approval_handler(
    callback_query: CallbackQuery,
    callback_data: BotCB,
    db: AsyncSession,
    state_data: dict,
    state: StateManager,
):
    await callback_query.message.edit(text=DialogText.ACTIONS_PROCESSING)
    await state.clear_state(db=db)
    sub = await Subscription.get_by_id(db, int(state_data["server_id"]))
    if not sub:
        update = await callback_query.message.answer(DialogText.SERVERS_NOT_FOUND, reply_markup=BotKB.subs_back())
        return await UserMessage.clear(update)

    servers = await Server.get_all(db)
    if not servers:
        update = await callback_query.message.answer(text=DialogText.SUBS_NO_SERVERS, reply_markup=BotKB.subs_back())
        return await UserMessage.add(update)

    kb = BotKB.subs_back(sub.id)
    if not callback_data.approval and state_data["sub_action"] != SubActionType.EXPIRE:
        return await callback_query.message.edit(text=DialogText.ACTIONS_FORGET, reply_markup=kb)

    match state_data["sub_action"]:
        case SubActionType.EXPIRE:
            await Subscription.update(
                db, sub=sub, expire=Subscription.generate_expire(int(state_data["expire"]), callback_data.approval)
            )
        case SubActionType.ENABLED_STATUS:
            if sub.is_active:
                client_update = await XUIManager.deactivate(servers=servers, uuid=sub.server_key)
            else:
                client_update = await XUIManager.activate(servers=servers, uuid=sub.server_key)
            if not client_update:
                update = await callback_query.message.answer(text=DialogText.SUBS_XUI_CLIENT_UPDATE_FAILED, reply_markup=kb)
                return await UserMessage.add(update)
            await Subscription.update(db, sub=sub, enabled=not sub.enabled)
        case SubActionType.REVOKE:
            new_uuid = Subscription.generate_server_key()
            client_update = await XUIManager.revoke(
                servers=servers, uuid=sub.server_key, new_uuid=new_uuid, enable=sub.is_active
            )
            if not client_update:
                update = await callback_query.message.answer(text=DialogText.SUBS_XUI_CLIENT_UPDATE_FAILED, reply_markup=kb)
                return await UserMessage.add(update)
            await Subscription.update(db, sub=sub, server_key=new_uuid)
        case SubActionType.RESET_USAGE:
            await Subscription.reset_usage(db, sub=sub)
        case SubActionType.REMOVE:
            client_delete = await XUIManager.remove(servers=servers, uuid=sub.server_key)
            if not client_delete:
                update = await callback_query.message.answer(text=DialogText.SUBS_XUI_CLIENT_DELETE_FAILED, reply_markup=kb)
                return await UserMessage.add(update)
            await Subscription.remove(db, sub=sub)
            kb = BotKB.subs_back()

    return await callback_query.message.edit(text=DialogText.ACTIONS_SUCCESS, reply_markup=kb)
