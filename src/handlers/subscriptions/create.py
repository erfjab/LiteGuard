from eiogram import Router
from eiogram.types import CallbackQuery, Message
from eiogram.filters import StateFilter, Text
from eiogram.state import StateManager, State, StateGroup

from src.keys import BotCB, BotKB, SectionType, ActionType
from src.db import AsyncSession, Server, UserMessage, Subscription
from src.lang import DialogText
from src.xui import XUIManager

router = Router()


class SubCreateForm(StateGroup):
    remark = State()
    expire = State()
    expire_type = State()
    limit_usage = State()


@router.callback_query(
    BotCB.filter(section=SectionType.SUBS, action=ActionType.CREATE),
)
async def sub_create_handler(callback_query: CallbackQuery, db: AsyncSession, state: StateManager):
    await state.set_state(db=db, state=SubCreateForm.remark)
    return await callback_query.message.edit(text=DialogText.SUBS_ENTER_REMARK, reply_markup=BotKB.subs_back())


@router.message(StateFilter(SubCreateForm.remark), Text())
async def sub_remark_handler(message: Message, db: AsyncSession, state: StateManager):
    if await Subscription.get_by_remark(db, message.text):
        update = await message.answer(
            text=DialogText.SUBS_REMARK_EXISTS,
        )
        return await UserMessage.add(update)
    await state.upsert_context(db=db, state=SubCreateForm.expire, remark=message.text)
    update = await message.answer(text=DialogText.SUBS_ENTER_EXPIRE, reply_markup=BotKB.subs_back())
    return await UserMessage.clear(update)


@router.message(StateFilter(SubCreateForm.expire), Text())
async def sub_expire_handler(message: Message, db: AsyncSession, state: StateManager):
    if not message.text[:-1].isdigit() or message.text[-1] not in ["d", "h"] or int(message.text[:-1]) <= 0:
        update = await message.answer(
            text=DialogText.SUBS_INVALID_EXPIRE,
        )
        return await UserMessage.add(update)
    expire = int(message.text[:-1]) * (24 * 3600 if message.text[-1] == "d" else 3600)
    await state.upsert_context(
        db=db,
        state=SubCreateForm.expire_type,
        expire=expire,
    )
    update = await message.answer(
        text=DialogText.SUBS_ASK_START_AFTER_FIRST_USE,
        reply_markup=BotKB.approval(section=SectionType.SUBS, action=ActionType.CREATE),
    )
    return await UserMessage.clear(update)


@router.callback_query(
    StateFilter(SubCreateForm.expire_type),
    BotCB.filter(section=SectionType.SUBS, action=ActionType.CREATE),
)
async def sub_expire_type_handler(callback_query: CallbackQuery, callback_data: BotCB, db: AsyncSession, state: StateManager):
    await state.upsert_context(
        db=db,
        state=SubCreateForm.expire_type,
        after_first_use=callback_data.approval,
    )
    return await callback_query.message.edit(
        text=DialogText.SUBS_ENTER_LIMIT_USAGE,
        reply_markup=BotKB.subs_back(),
    )


@router.message(StateFilter(SubCreateForm.limit_usage), Text())
async def sub_limit_usage_handler(message: Message, db: AsyncSession, state: StateManager, state_data: dict):
    if not message.text.isdigit() or int(message.text) <= 0:
        update = await message.answer(
            text=DialogText.SUBS_INVALID_LIMIT_USAGE,
        )
        return await UserMessage.add(update)
    client_uuid = Subscription.generate_key()
    client_created = await XUIManager.create(
        servers=await Server.get_all(db),
        uuid=client_uuid,
    )
    if not client_created:
        update = await message.answer(
            text=DialogText.SUBS_XUI_CLIENT_CREATE_FAILED,
        )
        return await UserMessage.add(update)
    sub = await Subscription.create(
        db,
        remark=state_data["remark"],
        access_key=Subscription.generate_key(),
        server_key=client_uuid,
        expire=Subscription.generate_expire(int(state_data["expire"]), state_data["after_first_use"]),
        limit_usage=int(message.text) * 1024 * 1024 * 1024,
        owner=message.from_user.id,
    )
    update = await message.answer(
        text=DialogText.ACTIONS_SUCCESS,
        reply_markup=BotKB.subs_back(sub.id),
    )
    await state.clear_state(db=db)
    return await UserMessage.clear(update)
