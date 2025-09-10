from enum import StrEnum


class DialogText(StrEnum):
    ### Commands
    COMMANDS_START = "🌟 <b>Welcome to LiteGuard!</b>\n💝 <a href='https://t.me/Magic_Mizban'>Project Sponsor: MagicMizban</a>"

    ### Actions
    ACTIONS_SUCCESS = "✅ Action completed successfully."
    ACTIONS_APPROVAL = "⚠️ <b>Are you sure you want to proceed with this action?</b>"
    ACTIONS_FORGET = "❌ Action cancelled. No changes were made."
    ACTIONS_PROCESSING = "⏳ Processing your request. Please wait..."
    ACTIONS_NOT_ALLOW = "❌ This action is not allowed."

    ### Servers
    SERVERS_MENU = "🖥 <b>Server Management</b>\nSelect a server to manage or add a new one."
    SERVERS_INFO = (
        "🖥 <b>Server Information</b>\nYou can update or delete the server from here.\n"
        "➖➖➖➖➖\n"
        "<b>Id:</b> <code>{id}</code>\n"
        "<b>Remark:</b> <code>{remark}</code>\n"
        "<b>Enabled:</b> <code>{enabled}</code>\n"
        "<b>CreatedAt:</b> <code>{created_at}</code>\n"
        "<b>Config:</b>\n<pre>{config}</pre>\n"
    )
    SERVERS_NOT_FOUND = "❌ No server found."
    SERVERS_ENTER_REMARK = "📝 <b>Enter a remark for the server:</b>\nThis helps you identify the server later."
    SERVERS_ENTER_CONFIG = "💻 <b>Enter the server configuration:</b>\n\n- username\n- password \n- host [{http or https}://{ip or domain}:{port}/{path}]\n- sub [{http or https}://{ip or domain}:{port}/{path}]\n\n<b>like:</b>\n<code>erfan erfan http://57.107.24.58:33431/u6QpcCkB5q8YdtGUx8 http://57.107.24.58:2096/sub </code>\n<code>admin admin https://dash.netshop.com:443/sd54ueRvx https://dash.netshop.com:443/sub </code>"
    SERVERS_REMARK_EXISTS = "❌ A server with this remark already exists. Please choose a different remark."
    SERVERS_INVALID_ACCESS = "❌ Failed to connect to the server. Please check the configuration and try again."
    SERVERS_INVALID_CONFIG_FORMAT = "❌ Invalid configuration format. Please follow the example provided."

    ### Subscriptions
    SUBS_MENU = "📦 <b>Subscription Management</b>\nSelect a subscription to manage or add a new one."
    SUBS_NOT_FOUND = "❌ No subscription found."
    SUBS_INFO = (
        "📦 <b>Subscription Information</b>\nYou can update or delete the subscription from here.\n"
        "➖➖➖➖➖\n"
        "<b>ID:</b> <code>{id}</code>\n"
        "<b>Remark:</b> <code>{remark}</code>\n"
        "<b>OwnerName:</b> <code>{owner}</code>\n"
        "➖➖➖➖➖\n"
        "<b>Enabled:</b> <code>{enabled}</code>\n"
        "<b>Availabled:</b> <code>{availabled}</code>\n"
        "➖➖➖➖➖\n"
        "<b>UsageLimit:</b> <code>{limit_usage}</code>\n"
        "<b>CurrentUsage:</b> <code>{current_usage}</code>\n"
        "<b>LifeTimeUsage:</b> <code>{lifetime_usage}</code>\n"
        "<b>LeftUsage:</b> <code>{left_usage}</code>\n"
        "➖➖➖➖➖\n"
        "<b>Expire:</b> <code>{expire}</code>\n"
        "➖➖➖➖➖\n"
        "<b>OnlineAt:</b> <code>{online_at}</code>\n"
        "<b>SubUpdate:</b> <code>{last_sub_updated_at}</code>\n"
        "<b>CreatedAt:</b> <code>{created_at}</code>\n"
        "<b>UpdatedAt:</b> <code>{updated_at}</code>\n"
        "➖➖➖➖➖\n"
        "<b>AccessLink:</b> <code>{link}</code>\n"
        "<b>ServerUsages:</b> \n<pre>{server_usages}</pre>\n"
    )
    SUBS_ENTER_REMARK = "📝 <b>Enter a remark for the subscription:</b>\nThis helps you identify the subscription later."
    SUBS_REMARK_EXISTS = "❌ A subscription with this remark already exists. Please choose a different remark."
    SUBS_ENTER_EXPIRE = "⏳ <b>Enter the expiration time for the subscription:</b>\nSend a number followed by a time unit (e.g., 30d for 30 days, 12h for 12 hours)."
    SUBS_INVALID_EXPIRE = (
        "❌ Invalid expiration format. Please send a number followed by 'd' for days or 'h' for hours (e.g., 30d or 12h)."
    )
    SUBS_ASK_START_AFTER_FIRST_USE = "🕒 <b>Should the subscription start after its first use?</b>\n\nIf yes, the expiration countdown will begin when the subscription is first used. If no, the countdown will start immediately upon creation."
    SUBS_ENTER_LIMIT_USAGE = "📊 <b>Enter the usage limit for the subscription:</b>\nSend a number representing the maximum allowed usage (e.g., 10 for 10 GB)."
    SUBS_INVALID_LIMIT_USAGE = "❌ Invalid usage limit. Please send a valid number (e.g., 10 for 10 GB)."
    SUBS_XUI_CLIENT_CREATE_FAILED = (
        "❌ Failed to create client on XUI server. Please check the server configuration and try again."
    )
    SUBS_NO_SERVERS = "❌ No servers available. Please add a server first."
    SUBS_QRCODE = (
        "📱 <b>Subscription QR Code</b>\n"
        "Scan the QR code below to access your subscription:\n"
        "<b>Remark:</b> <code>{remark} </code> [<code>{id}</code>]\n"
        "<b>UsageLimit:</b> <code>{limit_usage}</code>\n"
        "<b>Expire:</b> <code>{expire}</code>\n"
        "<b>Link:</b> {link}\n"
    )
    SUBS_XUI_CLIENT_UPDATE_FAILED = (
        "❌ Failed to update client on XUI server. Please check the server configuration and try again."
    )
    SUBS_XUI_CLIENT_DELETE_FAILED = (
        "❌ Failed to delete client on XUI server. Please check the server configuration and try again."
    )

    ### Settings
    SETTINGS_MENU = (
        "⚙️ <b>Settings Menu</b>\n"
        "Configure your LiteGuard settings below.\n"
        "➖➖➖➖➖\n"
        "<b>Shuffle:</b> <code>{shuffle}</code>\n"
        "<b>Placeholders:</b>{placeholders}\n"
        "<b>Informations:</b>{informations}\n"
    )
    SETTINGS_ENTER_PLACEHOLDER = (
        "📝 <b>Enter the placeholder text:</b>\n\n"
        "This text will be displayed when a subscription is unavailable or disabled.\n\n"
        "<b>Available variables:</b>\n"
        "• <code>{ID}</code> - Subscription ID\n"
        "• <code>{EMOJI}</code> - Subscription status emoji\n"
        "• <code>{REMARK}</code> - Subscription remark/username\n"
        "• <code>{LIMIT_USAGE}</code> - Usage limit (GB)\n"
        "• <code>{CURRENT_USAGE}</code> - Current usage (GB)\n"
        "• <code>{LIFETIME_USAGE}</code> - Total lifetime usage (GB)\n"
        "• <code>{LEFT_USAGE}</code> - Remaining usage (GB)\n"
        "• <code>{EXPIRE}</code> - Expiration date\n\n"
        "<b>Examples:</b>\n"
        "<code>⚠️ Subscription {REMARK} (ID: {ID}) is currently unavailable.</code>\n"
        "<code>Usage: {CURRENT_USAGE}/{LIMIT_USAGE} GB | Expires: {EXPIRE}</code>"
    )
    SETTINGS_SELECT_PLACEHOLDER = "⚙️ <b>Select a placeholder text:</b>"
    SETTINGS_SELECT_INFORMATION = "⚙️ <b>Select an information text:</b>"
    SETTINGS_ENTER_INFORMATION = (
        "📝 <b>Enter the information text:</b>\n\n"
        "This text will be displayed at the top of the subscription.\n\n"
        "<b>Available variables:</b>\n"
        "• <code>{ID}</code> - Subscription ID\n"
        "• <code>{EMOJI}</code> - Subscription status emoji\n"
        "• <code>{REMARK}</code> - Subscription remark/username\n"
        "• <code>{LIMIT_USAGE}</code> - Usage limit (GB)\n"
        "• <code>{CURRENT_USAGE}</code> - Current usage (GB)\n"
        "• <code>{LIFETIME_USAGE}</code> - Total lifetime usage (GB)\n"
        "• <code>{LEFT_USAGE}</code> - Remaining usage (GB)\n"
        "• <code>{EXPIRE}</code> - Expiration date\n"
        "• <code>{AVAILABLED}</code> - Availability status\n"
        "<b>Examples:</b>\n"
        "<code>🌟 username: {REMARK}!\n</code>"
        "<code>Enjoy your access with a limit of {LIMIT_USAGE} GB, valid until {EXPIRE}.</code>"
    )
    SETTINGS_NO_PLACEHOLDER = "❌ No placeholders available. Please add a placeholder first."
    SETTINGS_NO_INFORMATION = "❌ No informations available. Please add an information first."
