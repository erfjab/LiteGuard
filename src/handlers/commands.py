from eiogram import Router
from eiogram.types import Message
from eiogram.filters import Command, IgnoreStateFilter

from src.db import UserMessage
from src.lang import DialogText
from src.utils.depends import ClearState
from src.keys import BotKB

router = Router()


@router.message(Command("start"), IgnoreStateFilter())
async def start_handler(message: Message, _: ClearState):
    update = await message.answer(text=DialogText.COMMANDS_START, reply_markup=BotKB.home())
    return await UserMessage.clear(update)
