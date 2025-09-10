from eiogram import Router
from eiogram.types import CallbackQuery, Message
from eiogram.state import State, StateGroup, StateManager
from eiogram.filters import StateFilter, Text

from src.db import AsyncSession, Setting, UserMessage
from src.keys import BotKB, BotCB, SectionType, ActionType, SubActionType
from src.lang import DialogText

router = Router()


class SettingsUpdateForm(StateGroup):
    input = State()
    approval = State()
    select = State()


@router.callback_query(BotCB.filter(section=SectionType.SETTINGS, action=ActionType.UPDATE))
async def settings_update_handler(
    callback_query: CallbackQuery,
    callback_data: BotCB,
    db: AsyncSession,
    state: StateManager,
    setting: Setting,
):
    kb = BotKB.settings_back()
    _state = SettingsUpdateForm.input
    match callback_data.sub_action:
        case SubActionType.CREATE_PLACEHOLDER:
            text = DialogText.SETTINGS_ENTER_PLACEHOLDER
        case SubActionType.CREATE_INFORMATION:
            text = DialogText.SETTINGS_ENTER_INFORMATION
        case SubActionType.REMOVE_PLACEHOLDER:
            if not setting.placeholders:
                return await callback_query.answer(text=DialogText.SETTINGS_NO_PLACEHOLDER, show_alert=True)
            text = DialogText.SETTINGS_SELECT_PLACEHOLDER
            kb = BotKB.remove_placeholder(setting)
            _state = SettingsUpdateForm.select
        case SubActionType.REMOVE_INFORMATION:
            if not setting.informations:
                return await callback_query.answer(text=DialogText.SETTINGS_NO_INFORMATION, show_alert=True)
            text = DialogText.SETTINGS_SELECT_INFORMATION
            kb = BotKB.remove_information(setting)
            _state = SettingsUpdateForm.select
        case SubActionType.SHUFFLE:
            text = DialogText.ACTIONS_APPROVAL
            kb = BotKB.approval(section=SectionType.SETTINGS, action=ActionType.UPDATE, target=setting.id)
            _state = SettingsUpdateForm.approval
    await state.upsert_context(db=db, state=_state, sub_action=callback_data.sub_action)
    return await callback_query.message.edit(text=text, reply_markup=kb)


@router.message(StateFilter(SettingsUpdateForm.input), Text())
async def input_handler(message: Message, db: AsyncSession, state_data: dict, state: StateManager, setting: Setting):
    kb = BotKB.settings_back()
    match state_data["sub_action"]:
        case SubActionType.CREATE_PLACEHOLDER:
            setting.placeholders.append(message.text)
            await Setting.update(db, placeholders=setting.placeholders)
        case SubActionType.CREATE_INFORMATION:
            setting.informations.append(message.text)
            await Setting.update(db, informations=setting.informations)

    await state.clear_state(db=db)
    update = await message.answer(text=DialogText.ACTIONS_SUCCESS, reply_markup=kb)
    return await UserMessage.clear(update)


@router.callback_query(
    BotCB.filter(section=SectionType.SETTINGS, action=ActionType.UPDATE),
    StateFilter(SettingsUpdateForm.select),
)
async def select_handler(
    callback_query: CallbackQuery,
    callback_data: BotCB,
    db: AsyncSession,
    state_data: dict,
    state: StateManager,
    setting: Setting,
):
    kb = BotKB.settings_back()
    match state_data["sub_action"]:
        case SubActionType.REMOVE_PLACEHOLDER:
            if 0 <= int(callback_data.target) < len(setting.placeholders):
                setting.placeholders.pop(int(callback_data.target))
                await Setting.update(db, placeholders=setting.placeholders)
        case SubActionType.REMOVE_INFORMATION:
            if 0 <= int(callback_data.target) < len(setting.informations):
                setting.informations.pop(int(callback_data.target))
                await Setting.update(db, informations=setting.informations)

    await state.clear_state(db=db)
    return await callback_query.message.edit(text=DialogText.ACTIONS_SUCCESS, reply_markup=kb)


@router.callback_query(
    BotCB.filter(section=SectionType.SETTINGS, action=ActionType.UPDATE),
    StateFilter(SettingsUpdateForm.approval),
)
async def approval_handler(
    callback_query: CallbackQuery,
    callback_data: BotCB,
    db: AsyncSession,
    state_data: dict,
    state: StateManager,
    setting: Setting,
):
    await state.clear_state(db=db)
    kb = BotKB.settings_back()
    if not callback_data.approval:
        return await callback_query.message.edit(text=DialogText.ACTIONS_FORGET, reply_markup=kb)

    match state_data["sub_action"]:
        case SubActionType.SHUFFLE:
            setting = await Setting.update(db, shuffle=not setting.shuffle)

    return await callback_query.message.edit(text=DialogText.ACTIONS_SUCCESS, reply_markup=kb)
