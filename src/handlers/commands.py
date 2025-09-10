from eiogram import Router
from eiogram.types import Message, CallbackQuery
from eiogram.filters import Command, IgnoreStateFilter

from src.db import UserMessage
from src.lang import DialogText
from src.utils.depends import ClearState
from src.keys import BotKB, BotCB, SectionType, ActionType

router = Router()


@router.message(Command("start"), IgnoreStateFilter())
async def start_handler(message: Message, _: ClearState):
    update = await message.answer(text=DialogText.COMMANDS_START, reply_markup=BotKB.home())
    return await UserMessage.clear(update)


@router.callback_query(BotCB.filter(section=SectionType.HOME, action=ActionType.MENU))
async def home_menu_handler(callback_query: CallbackQuery, _: ClearState):
    update = await callback_query.message.edit(text=DialogText.COMMANDS_START, reply_markup=BotKB.home())
    return await UserMessage.clear(update, keep_current=True)
