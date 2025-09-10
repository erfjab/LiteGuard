from enum import StrEnum


class ButtonText(StrEnum):
    ### actions
    ACTIONS_BACK = "🔙 Back"
    ACTIONS_CREATE = "➕ Create"
    ACTIONS_YES = "✔️ Yes"
    ACTIONS_NO = "✖️ No"

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

    ### SubActions
    REMARK = "📝 Remark"
    CHANGE_CONFIG = "⚙️ Change Config"
    ACTIVATED = "✔️ Activated"
    DEACTIVATED = "✖️ Deactivated"
    REMOVE = "🗑️ Remove"
    EXPIRE = "🕒 Expire"
    USAGE_LIMIT = "📊 Usage Limit"
    RESET_USAGE = "🔄 Reset Usage"
    REVOKE = "🚫 Revoke"
    QRCODE = "🆔 QR Code"
    ACTIVATED_SHUFFLE = "✔️ Activated Shuffle"
    DISABLED_SHUFFLE = "✖️ Deactivated Shuffle"
    CREATE_PLACEHOLDER = "➕ Placeholder"
    CREATE_INFORMATION = "➕ Information"
    REMOVE_PLACEHOLDER = "🗑️ Placeholder"
    REMOVE_INFORMATION = "🗑️ Information"
