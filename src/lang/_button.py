from enum import StrEnum


class ButtonText(StrEnum):
    ### actions
    ACTIONS_BACK = "🔙 Back"
    ACTIONS_CREATE = "➕ Create"

    ### pages
    PAGES_BACK = "⬅️"
    PAGES_NEXT = "➡️"

    ### sections
    SERVERS = "🖥️ Servers"
    STATS = "☄️ Stats"
    USERS = "👤 Users"
    SUBS = "📥 Subscriptions"
    SETTING = "⚙️ Settings"
    API_KEYS = "🔑 API Keys"
    TEST = "🧪 Test"
    OWNER = "🌚  Owner"
    ISSUE = "🐞 Report Issue"
