from enum import StrEnum


class DialogText(StrEnum):
    ### Commands
    COMMANDS_START = "🌟 <b>Welcome to LiteGuard!</b>\n💝 <a href='https://t.me/Magic_Mizban'>Project Sponsor: MagicMizban</a>"

    ### Actions
    ACTIONS_SUCCESS = "✅ Action completed successfully."
    ACTIONS_APPROVAL = "⚠️ <b>Are you sure you want to proceed with this action?</b>"
    ACTIONS_FORGET = "❌ Action cancelled. No changes were made."

    ### Servers
    SERVERS_MENU = (
        "🖥 <b>Server Management</b>\nSelect a server to manage or add a new one."
    )
    SERVERS_INFO = (
        "🖥 <b>Server Information</b>\nYou can update or delete the server from here.\n"
        "<b>Id:</b> <code>{id}</code>\n"
        "<b>Remark:</b> <code>{remark}</code>\n"
        "<b>Enabled:</b> <code>{enabled}</code>\n"
        "<b>CreatedAt:</b> <code>{created_at}</code>\n"
        "<b>Config:</b>\n<pre>{config}</pre>\n"
    )
    SERVERS_NOT_FOUND = "❌ No server found."
    SERVERS_ENTER_REMARK = "📝 <b>Enter a remark for the new server:</b>\nThis helps you identify the server later."
    SERVERS_ENTER_CONFIG = "💻 <b>Enter the server configuration:</b>\n\n- username\n- password \n- host [{http or https}://{ip or domain}:{port}/{path}]\n\n<b>like:</b>\n<code>erfan erfan http://57.107.24.58:33431/u6QpcCkB5q8YdtGUx8</code>\n<code>admin admin https://dash.netshop.com:443/sd54ueRvx</code>"
    SERVERS_REMARK_EXISTS = (
        "❌ A server with this remark already exists. Please choose a different remark."
    )
    SERVERS_INVALID_ACCESS = "❌ Failed to connect to the server. Please check the configuration and try again."
    SERVERS_INVALID_CONFIG_FORMAT = (
        "❌ Invalid configuration format. Please follow the example provided."
    )
