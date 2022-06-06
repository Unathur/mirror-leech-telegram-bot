from threading import Thread
from telegram import InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler

from bot import LOGGER, dispatcher
from bot.helper.mirror_utils.upload_utils.gdriveTools import GoogleDriveHelper
from bot.helper.telegram_helper.message_utils import sendMessage, editMessage, sendMarkup
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper import button_build

def list_buttons(update, context):
    user_id = update.message.from_user.id
    if len(update.message.text.split(" ", maxsplit=1)) < 2:
        return sendMessage('𝐒𝐞𝐧𝐝 𝐚 𝐬𝐞𝐚𝐫𝐜𝐡 𝐤𝐞𝐲 𝐚𝐥𝐨𝐧𝐠 𝐰𝐢𝐭𝐡 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 🙄', context.bot, update.message)
    buttons = button_build.ButtonMaker()
    buttons.sbutton("ғᴏʟᴅᴇʀs", f"types {user_id} folders")
    buttons.sbutton("ғɪʟᴇs", f"types {user_id} files")
    buttons.sbutton("ʙᴏᴛʜ", f"types {user_id} both")
    buttons.sbutton("ᴄᴀɴᴄᴇʟ", f"types {user_id} cancel")
    button = InlineKeyboardMarkup(buttons.build_menu(2))
    sendMarkup('Choose option to list.', context.bot, update.message, button)

def select_type(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    msg = query.message
    key = msg.reply_to_message.text.split(" ", maxsplit=1)[1]
    data = query.data
    data = data.split(" ")
    if user_id != int(data[1]):
        return query.answer(text="Not Yours!", show_alert=True)
    elif data[2] == 'cancel':
        query.answer()
        return editMessage("𝐥𝐢𝐬𝐭 𝐡𝐚𝐬 𝐛𝐞𝐞𝐧 𝐜𝐚𝐧𝐜𝐞𝐥𝐞𝐝!👀", msg)
    query.answer()
    item_type = data[2]
    editMessage(f"<b>𝐒𝐞𝐚𝐫𝐜𝐡𝐢𝐧𝐠 𝐟𝐨𝐫 <i>{key}</i> 𝐏𝐥𝐞𝐚𝐬𝐞 𝐖𝐚𝐢𝐭...</b>", msg)
    Thread(target=_list_drive, args=(key, msg, item_type)).start()

def _list_drive(key, bmsg, item_type):
    LOGGER.info(f"listing: {key}")
    gdrive = GoogleDriveHelper()
    msg, button = gdrive.drive_list(key, isRecursive=True, itemType=item_type)
    if button:
        editMessage(msg, bmsg, button)
    else:
        editMessage(f'😐 𝐍𝐨 𝐫𝐞𝐬𝐮𝐥𝐭 𝐟𝐨𝐮𝐧𝐝 𝐟𝐨𝐫 <i>{key}</i>', bmsg)

list_handler = CommandHandler(BotCommands.ListCommand, list_buttons, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
list_type_handler = CallbackQueryHandler(select_type, pattern="types", run_async=True)
dispatcher.add_handler(list_handler)
dispatcher.add_handler(list_type_handler)
