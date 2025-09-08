from enum import StrEnum


class ButtonText(StrEnum):
    ### actions
    ACTIONS_BACK = "🔙 Back"
    ACTIONS_CREATE = "➕ Create"
    ACTIONS_CONFIRM = "✅ Confirm"
    ACTIONS_CANCEL = "❌ Cancel"

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
