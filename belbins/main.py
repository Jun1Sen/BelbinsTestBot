
from aiogram_dialog import setup_dialogs
from aiogram_dialog.widgets.text import Const # Здесь будем импортировать нужные виджеты
from dispatcher import dp, bot
from handlers import start_dialog

dp.include_router(start_dialog)
setup_dialogs(dp)
dp.run_polling(bot)