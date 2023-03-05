from aiogram import types


# Стартовые клавиатуры

# Main Start

def main_menu_keyboard():
    buttons = [
        types.InlineKeyboardButton(text="❓ Помощь", callback_data="help"),
        types.InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings"),
        types.InlineKeyboardButton(text="💰 Пополнить баланс", callback_data="top_up")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


def buy_keyboard(amount):
    buttons = [
        types.InlineKeyboardButton(text="✅ Да", callback_data=f"buy&{amount}"),
        types.InlineKeyboardButton(text="❌ Нет", callback_data="go_to_main_menu")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


def go_to_main_menu():
    buttons = [
        types.InlineKeyboardButton(text="⏪ В главное меню", callback_data="go_to_main_menu")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


def go_to_main_menu_if_new():
    buttons = [
        types.InlineKeyboardButton(text="⏩ В главное меню", callback_data="go_to_main_menu")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


def edit_parameter_keyboard(parameter, action, value):
    if action == "regular":
        buttons = [
            types.InlineKeyboardButton(text="➕", callback_data=f"edit_parameter&plus&{parameter}&{value}"),
            types.InlineKeyboardButton(text="➖", callback_data=f"edit_parameter&minus&{parameter}&{value}"),
            types.InlineKeyboardButton(text="Готово", callback_data=f"set_parameter&{parameter}&{value}")
        ]
    elif action == "max":
        buttons = [
            types.InlineKeyboardButton(text="➖", callback_data=f"edit_parameter&minus&{parameter}&{value}"),
            types.InlineKeyboardButton(text="Готово", callback_data=f"set_parameter&{parameter}&{value}")
        ]
    else:
        buttons = [
            types.InlineKeyboardButton(text="➕", callback_data=f"edit_parameter&plus&{parameter}&{value}"),
            types.InlineKeyboardButton(text="Готово", callback_data=f"set_parameter&{parameter}&{value}")
        ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


def choose_parameter_keyboard(users_temperature, frequency_penalty, presence_penalty):
    buttons = [
        types.InlineKeyboardButton(text="Temperature",
                                   callback_data=f"edit_parameter&regular&temperature&{users_temperature}"),
        types.InlineKeyboardButton(text="Frequency penalty",
                                   callback_data=f"edit_parameter&regular&frequency_penalty&{frequency_penalty}"),
        types.InlineKeyboardButton(text="Presence penalty",
                                   callback_data=f"edit_parameter&regular&presence_penalty&{presence_penalty}"),
        types.InlineKeyboardButton(text="⏪ В главное меню",
                                   callback_data=f"go_to_main_menu")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


def parameter_update_done_keyboard():
    buttons = [
        types.InlineKeyboardButton(text="⏪ В меню настроек", callback_data="settings")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


# Команды хелпер клава

def commands_helper_keyboard():
    kb = [
        [types.KeyboardButton(text="/start — Вызвать меню")],
        [types.KeyboardButton(text="/clear — Очистить историю диалога")],
        # [types.KeyboardButton(text="/img — Сгенерировать картинку")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    return keyboard
