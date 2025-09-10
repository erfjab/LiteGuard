from typing import List, Optional, Dict
from eiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from eiogram.utils import InlineKeyboardBuilder
from src.db import Server, Subscription, Setting
from src.utils.pagination import Pagination
from src.lang import ButtonText
from .callbacks import BotCB
from .enums import SectionType, ActionType, SubActionType


class BotKB:
    @classmethod
    def _back(
        cls,
        section: SectionType = SectionType.HOME,
        target: Optional[str | int] = None,
    ) -> InlineKeyboardButton:
        return InlineKeyboardButton(
            text=ButtonText.ACTIONS_BACK,
            callback_data=BotCB(
                section=section,
                action=ActionType.INFO if target else ActionType.MENU,
                target=target,
            ).pack(),
        )

    @classmethod
    def _create(
        cls,
        section: SectionType = SectionType.HOME,
    ) -> InlineKeyboardButton:
        return InlineKeyboardButton(
            text=ButtonText.ACTIONS_CREATE,
            callback_data=BotCB(section=section, action=ActionType.CREATE).pack(),
        )

    @classmethod
    def _back_generate(
        cls,
        section: SectionType = SectionType.HOME,
        target: Optional[int | str] = None,
    ) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.row(cls._back(section=section, target=target))
        return kb.as_markup()

    @classmethod
    def _menu(
        cls,
        items: Dict[str, int | str],
        section: SectionType,
        pagination: Optional[Pagination] = None,
        create: bool = True,
    ) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        for remark, target in items.items():
            kb.add(
                text=remark,
                callback_data=BotCB(
                    section=section,
                    action=ActionType.INFO,
                    target=target,
                ).pack(),
            )
        kb.adjust(2)
        if pagination and (pagination.back or pagination.next):
            kb.row(
                *cls._pagination(
                    pagination=pagination,
                    section=section,
                    action=ActionType.MENU,
                ),
                size=2,
            )
        if create:
            kb.row(cls._create(section=section))
        kb.row(cls._back())
        return kb.as_markup()

    @classmethod
    def _update(
        cls,
        section: SectionType,
        target: str | int,
        updates: Dict[str, str],
    ) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        for sub_action, text in updates.items():
            kb.add(
                text=text,
                callback_data=BotCB(
                    section=section,
                    action=ActionType.UPDATE,
                    target=target,
                    sub_action=sub_action,
                ).pack(),
            )
        kb.adjust(2)
        kb.row(cls._back(section=section))
        return kb.as_markup()

    @classmethod
    def _pagination(
        cls,
        pagination: Pagination,
        section: SectionType,
        action: ActionType = ActionType.MENU,
    ) -> List[InlineKeyboardButton]:
        buttons = []
        buttons.append(
            InlineKeyboardButton(
                text=ButtonText.PAGES_BACK if pagination.back else "     ",
                callback_data=BotCB(section=section, action=action).pack() if pagination.back else "_",
            )
        )
        buttons.append(
            InlineKeyboardButton(
                text=ButtonText.PAGES_NEXT if pagination.next else "     ",
                callback_data=BotCB(section=section, action=action).pack() if pagination.next else "_",
            )
        )
        return buttons

    @classmethod
    def home(cls) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        items = {
            SectionType.STATS: ButtonText.STATS,
            SectionType.SUBS: ButtonText.SUBS,
            SectionType.SERVERS: ButtonText.SERVERS,
            SectionType.SETTINGS: ButtonText.SETTING,
        }
        for section, remark in items.items():
            kb.add(
                text=remark,
                callback_data=BotCB(section=section, action=ActionType.MENU).pack(),
            )
        kb.add(text=ButtonText.OWNER, url="https://t.me/erfjabs")
        kb.add(text=ButtonText.ISSUE, url="https://github.com/erfjab/LiteGuard/issues")
        kb.adjust(1, 2, 1, 2, 1, 2)
        return kb.as_markup()

    @classmethod
    def servers_menu(cls, pagination: Pagination) -> InlineKeyboardMarkup:
        return cls._menu(
            items={item.kb_remark: item.id for item in pagination.items},
            section=SectionType.SERVERS,
            pagination=pagination,
        )

    @classmethod
    def servers_update(cls, item: Server) -> InlineKeyboardMarkup:
        return cls._update(
            section=SectionType.SERVERS,
            target=item.id,
            updates={
                SubActionType.REMARK: ButtonText.REMARK,
                SubActionType.ENABLED_STATUS: ButtonText.DEACTIVATED if item.enabled else ButtonText.ACTIVATED,
                SubActionType.CHANGE_CONFIG: ButtonText.CHANGE_CONFIG,
                SubActionType.REMOVE: ButtonText.REMOVE,
            },
        )

    @classmethod
    def servers_back(cls, target: Optional[int | str] = None) -> InlineKeyboardMarkup:
        return cls._back_generate(section=SectionType.SERVERS, target=target)

    @classmethod
    def approval(
        cls,
        section: SectionType,
        action: ActionType = ActionType.UPDATE,
        target: Optional[int] = None,
    ):
        kb = InlineKeyboardBuilder()
        kb.add(
            text=ButtonText.ACTIONS_YES,
            callback_data=BotCB(section=section, action=action, approval=True).pack(),
        )
        kb.add(
            text=ButtonText.ACTIONS_NO,
            callback_data=BotCB(section=section, action=action, approval=False).pack(),
        )
        kb.adjust(2)
        kb.row(cls._back(section=section, target=target), size=1)
        return kb.as_markup()

    @classmethod
    def subs_menu(cls, pagination: Pagination) -> InlineKeyboardMarkup:
        return cls._menu(
            items={item.kb_remark: item.id for item in pagination.items},
            section=SectionType.SUBS,
            pagination=pagination,
        )

    @classmethod
    def subs_update(cls, item: Subscription) -> InlineKeyboardMarkup:
        return cls._update(
            section=SectionType.SUBS,
            target=item.id,
            updates={
                SubActionType.REMARK: ButtonText.REMARK,
                SubActionType.ENABLED_STATUS: ButtonText.DEACTIVATED if item.enabled else ButtonText.ACTIVATED,
                SubActionType.EXPIRE: ButtonText.EXPIRE,
                SubActionType.USAGE_LIMIT: ButtonText.USAGE_LIMIT,
                SubActionType.RESET_USAGE: ButtonText.RESET_USAGE,
                SubActionType.REVOKE: ButtonText.REVOKE,
                SubActionType.QRCODE: ButtonText.QRCODE,
                SubActionType.REMOVE: ButtonText.REMOVE,
            },
        )

    @classmethod
    def subs_back(cls, target: Optional[int | str] = None) -> InlineKeyboardMarkup:
        return cls._back_generate(section=SectionType.SUBS, target=target)

    @classmethod
    def settings_back(cls) -> InlineKeyboardMarkup:
        return cls._back_generate(section=SectionType.SETTINGS)

    @classmethod
    def settings_menu(cls, setting: Setting) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        updates = {
            SubActionType.SHUFFLE: ButtonText.DISABLED_SHUFFLE if setting.shuffle else ButtonText.ACTIVATED_SHUFFLE,
            SubActionType.CREATE_PLACEHOLDER: ButtonText.CREATE_PLACEHOLDER,
            SubActionType.REMOVE_PLACEHOLDER: ButtonText.REMOVE_PLACEHOLDER,
            SubActionType.CREATE_INFORMATION: ButtonText.CREATE_INFORMATION,
            SubActionType.REMOVE_INFORMATION: ButtonText.REMOVE_INFORMATION,
        }
        for sub_action, text in updates.items():
            kb.add(
                text=text,
                callback_data=BotCB(
                    section=SectionType.SETTINGS,
                    action=ActionType.UPDATE,
                    sub_action=sub_action,
                ).pack(),
            )
        kb.adjust(1, 2, 2)
        kb.row(cls._back(), size=1)
        return kb.as_markup()

    @classmethod
    def remove_placeholder(cls, setting: Setting) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        for idx, remark in enumerate(setting.placeholders):
            kb.add(
                text=remark,
                callback_data=BotCB(
                    section=SectionType.SETTINGS,
                    action=ActionType.UPDATE,
                    target=idx,
                ).pack(),
            )
        kb.adjust(1)
        kb.row(cls._back(section=SectionType.SETTINGS), size=1)
        return kb.as_markup()

    @classmethod
    def remove_information(cls, setting: Setting) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        for idx, remark in enumerate(setting.informations):
            kb.add(
                text=remark,
                callback_data=BotCB(
                    section=SectionType.SETTINGS,
                    action=ActionType.UPDATE,
                    target=idx,
                ).pack(),
            )
        kb.adjust(1)
        kb.row(cls._back(section=SectionType.SETTINGS), size=1)
        return kb.as_markup()
