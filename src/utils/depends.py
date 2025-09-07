from typing import Annotated

from eiogram.utils.depends import Depends
from eiogram.state import StateManager

from src.db import AsyncSession


async def _clear_state(db: AsyncSession, state: StateManager) -> None:
    await state.clear_state(db=db)


ClearState = Annotated[None, Depends(_clear_state)]
