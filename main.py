from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ContentTypes
from aiogram.utils import executor

import colorama
from colorama import Fore, Back, Style

import asyncio

import logging

from config import *
from db_content import *
from db_users import *
from open_ai_api import *
from keyboards import *
from payments import *
from texts import *
from utils import *

colorama.init()

bot = Bot(token=bot_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

logging.basicConfig(level=logging.INFO)


@dp.message_handler(lambda message: message.chat.type == 'private', content_types=types.ContentTypes.TEXT,
                    regexp="/clear")
async def handler(message: types.Message):
    delete_record(message.from_user.id)
    await message.reply(session_clear_text)


@dp.message_handler(lambda message: message.chat.type == 'group', content_types=types.ContentTypes.TEXT,
                    regexp="/clear")
async def handle_group_messages(message: types.Message):
    delete_record(message.chat.id)
    await message.reply(session_clear_text)


@dp.message_handler(lambda message: message.chat.type == 'supergroup', content_types=types.ContentTypes.TEXT,
                    regexp="/clear")
async def handle_group_messages(message: types.Message):
    delete_record(message.chat.id)
    await message.reply(session_clear_text)


@dp.message_handler(lambda message: message.chat.type == 'private', content_types=types.ContentTypes.TEXT,
                    regexp="/start")
async def handler(message: types.Message):
    if not user_exists(message.from_user.id):
        create_user(message.from_user.id, message.from_user.username)
        await message.answer(for_new_users, parse_mode="Markdown", reply_markup=go_to_main_menu_if_new())
        await message.answer(commands_helper_text, reply_markup=commands_helper_keyboard())
    else:
        tokens = get_from_user(message.from_user.id, "balance")
        await message.answer(main_menu_text(tokens), parse_mode="Markdown", reply_markup=main_menu_keyboard())


@dp.message_handler(lambda message: message.chat.type == 'group', content_types=types.ContentTypes.TEXT,
                    regexp="/start")
async def handle_group_messages(message: types.Message):
    await message.answer(only_in_private_text(), parse_mode="Markdown")


@dp.message_handler(lambda message: message.chat.type == 'supergroup', content_types=types.ContentTypes.TEXT,
                    regexp="/start")
async def handle_group_messages(message: types.Message):
    await message.answer(only_in_private_text(), parse_mode="Markdown")


@dp.callback_query_handler(text="go_to_main_menu")
async def top_up_started(call: types.CallbackQuery):
    tokens = get_from_user(call.from_user.id, "balance")
    await call.message.edit_text(main_menu_text(tokens), parse_mode="Markdown", reply_markup=main_menu_keyboard())


@dp.message_handler(lambda message: message.chat.type == 'private', content_types=types.ContentTypes.TEXT)
async def handle_group_messages(message: types.Message):
    print(Fore.BLUE + "private")
    print(Style.RESET_ALL)
    if get_from_user(message.from_user.id, "balance") > balance_threshold:
        if chat_id_exists(message.from_user.id):
            msg = await message.reply(waiting_for_the_answer_text, parse_mode="Markdown")
            update_messages(message.from_user.id, "user", message.text)
            messages_for_response = get_messages(message.from_user.id)
            response = await asyncio.get_running_loop().run_in_executor(None, get_response,
                                                                        messages_for_response,
                                                                        message.from_user.id,
                                                                        message.from_user.id)
            await bot.delete_message(msg.chat.id, msg.message_id)
            if response[0]:
                await message.reply(response[1])
                if get_total_tokens(message.from_user.id) > prompt_is_big_threshold:
                    await message.reply(dont_forget_to_clear_text, parse_mode="Markdown")
                update_messages(message.from_user.id, "assistant", response[1])
            else:
                if response[1] == "APIError":
                    await message.reply(errors_response_texts(response[1]), parse_mode="Markdown")
                elif response[1] == "RateLimitError":
                    await message.reply(errors_response_texts(response[1]), parse_mode="Markdown")
                elif response[1] == "InvalidRequestError":
                    await message.reply(errors_response_texts(response[1]), parse_mode="Markdown")
                    delete_record(message.from_user.id)
                else:
                    await message.reply(unknown_error_response_text, parse_mode="Markdown")
                    delete_record(message.from_user.id)
        else:
            create_messages(message.from_user.id, message.text)
            msg = await message.reply(waiting_for_the_answer_text, parse_mode="Markdown")
            messages_for_response = get_messages(message.from_user.id)
            response = await asyncio.get_running_loop().run_in_executor(None, get_response,
                                                                        messages_for_response,
                                                                        message.from_user.id,
                                                                        message.from_user.id)
            await bot.delete_message(msg.chat.id, msg.message_id)
            if response[0]:
                await message.reply(response[1])
                if get_total_tokens(message.from_user.id) > prompt_is_big_threshold:
                    await message.reply(dont_forget_to_clear_text, parse_mode="Markdown")
                update_messages(message.from_user.id, "assistant", response[1])
            else:
                if response[1] == "APIError":
                    await message.reply(errors_response_texts(response[1]), parse_mode="Markdown")
                elif response[1] == "RateLimitError":
                    await message.reply(errors_response_texts(response[1]), parse_mode="Markdown")
                elif response[1] == "InvalidRequestError":
                    await message.reply(errors_response_texts(response[1]), parse_mode="Markdown")
                    delete_record(message.from_user.id)
                else:
                    await message.reply(unknown_error_response_text, parse_mode="Markdown")
                    delete_record(message.from_user.id)
    else:
        await message.reply(private_balance_low_text, parse_mode="Markdown")


@dp.message_handler(lambda message: message.chat.type == 'group', content_types=types.ContentTypes.TEXT,
                    regexp=bot_name)
async def handle_group_messages(message: types.Message):
    print(Fore.BLUE + "group")
    print(Style.RESET_ALL)
    chat_admins = await bot.get_chat_administrators(message.chat.id)
    creator_id = "unknown"
    for i in range(len(chat_admins)):
        if chat_admins[i]['status'] == "creator":
            creator_id = chat_admins[i]['user']['id']
    creator_is_member = await bot.get_chat_member(message.chat.id, creator_id)
    creator_is_member_id = creator_is_member['user']['id']
    if creator_id == creator_is_member_id:
        if get_from_user(creator_id, "balance") > balance_threshold:
            updated_text = message.text.split(bot_name)[1]
            if chat_id_exists(message.chat.id):
                msg = await message.reply(waiting_for_the_answer_text, parse_mode="Markdown")
                update_messages(message.chat.id, "user", updated_text)
                messages_for_response = get_messages(message.chat.id)
                response = await asyncio.get_running_loop().run_in_executor(None, get_response,
                                                                            messages_for_response,
                                                                            creator_id,
                                                                            message.chat.id)
                await bot.delete_message(msg.chat.id, msg.message_id)
                if response[0]:
                    await message.reply(response[1])
                    if get_total_tokens(message.chat.id) > prompt_is_big_threshold:
                        await message.reply(dont_forget_to_clear_text, parse_mode="Markdown")
                    update_messages(message.chat.id, "assistant", response[1])
                else:
                    if response[1] == "APIError":
                        await message.reply(errors_response_texts(response[1]), parse_mode="Markdown")
                    elif response[1] == "RateLimitError":
                        await message.reply(errors_response_texts(response[1]), parse_mode="Markdown")
                    elif response[1] == "InvalidRequestError":
                        await message.reply(errors_response_texts(response[1]), parse_mode="Markdown")
                        delete_record(message.chat.id)
                    else:
                        await message.reply(unknown_error_response_text, parse_mode="Markdown")
                        delete_record(message.chat.id)
            else:
                create_messages(message.chat.id, updated_text)
                msg = await message.reply(waiting_for_the_answer_text, parse_mode="Markdown")
                messages_for_response = get_messages(message.chat.id)
                response = await asyncio.get_running_loop().run_in_executor(None, get_response,
                                                                            messages_for_response,
                                                                            creator_id,
                                                                            message.chat.id)
                await bot.delete_message(msg.chat.id, msg.message_id)
                if response[0]:
                    await message.reply(response[1])
                    if get_total_tokens(message.chat.id) > prompt_is_big_threshold:
                        await message.reply(dont_forget_to_clear_text, parse_mode="Markdown")
                    update_messages(message.chat.id, "assistant", response[1])
                else:
                    if response[1] == "APIError":
                        await message.reply(errors_response_texts(response[1]), parse_mode="Markdown")
                    elif response[1] == "RateLimitError":
                        await message.reply(errors_response_texts(response[1]), parse_mode="Markdown")
                    elif response[1] == "InvalidRequestError":
                        await message.reply(errors_response_texts(response[1]), parse_mode="Markdown")
                        delete_record(message.chat.id)
                    else:
                        await message.reply(unknown_error_response_text, parse_mode="Markdown")
                        delete_record(message.chat.id)
        else:
            await message.reply(admins_balance_low_text, parse_mode="Markdown")
    else:
        await message.reply(work_in_public_chat_error, parse_mode="Markdown")


@dp.message_handler(lambda message: message.chat.type == 'supergroup', content_types=types.ContentTypes.TEXT,
                    regexp=bot_name)
async def handle_group_messages(message: types.Message):
    print(Fore.BLUE + "supergroup")
    print(Style.RESET_ALL)
    chat_admins = await bot.get_chat_administrators(message.chat.id)
    creator_id = "unknown"
    for i in range(len(chat_admins)):
        if chat_admins[i]['status'] == "creator":
            creator_id = chat_admins[i]['user']['id']
    creator_is_member = await bot.get_chat_member(message.chat.id, creator_id)
    creator_is_member_id = creator_is_member['user']['id']
    if creator_id == creator_is_member_id:
        if get_from_user(creator_id, "balance") > balance_threshold:
            updated_text = message.text.split(bot_name)[1]
            if chat_id_exists(message.chat.id):
                msg = await message.reply(waiting_for_the_answer_text, parse_mode="Markdown")
                update_messages(message.chat.id, "user", updated_text)
                messages_for_response = get_messages(message.chat.id)
                response = await asyncio.get_running_loop().run_in_executor(None, get_response,
                                                                            messages_for_response,
                                                                            creator_id,
                                                                            message.chat.id)
                await bot.delete_message(msg.chat.id, msg.message_id)
                if response[0]:
                    await message.reply(response[1])
                    if get_total_tokens(message.chat.id) > prompt_is_big_threshold:
                        await message.reply(dont_forget_to_clear_text, parse_mode="Markdown")
                    update_messages(message.chat.id, "assistant", response[1])
                else:
                    if response[1] == "APIError":
                        await message.reply(errors_response_texts(response[1]), parse_mode="Markdown")
                    elif response[1] == "RateLimitError":
                        await message.reply(errors_response_texts(response[1]), parse_mode="Markdown")
                    elif response[1] == "InvalidRequestError":
                        await message.reply(errors_response_texts(response[1]), parse_mode="Markdown")
                        delete_record(message.chat.id)
                    else:
                        await message.reply(unknown_error_response_text, parse_mode="Markdown")
                        delete_record(message.chat.id)
            else:
                create_messages(message.chat.id, updated_text)
                msg = await message.reply(waiting_for_the_answer_text, parse_mode="Markdown")
                messages_for_response = get_messages(message.chat.id)
                response = await asyncio.get_running_loop().run_in_executor(None, get_response,
                                                                            messages_for_response,
                                                                            creator_id,
                                                                            message.chat.id)
                await bot.delete_message(msg.chat.id, msg.message_id)
                if response[0]:
                    await message.reply(response[1])
                    if get_total_tokens(message.chat.id) > prompt_is_big_threshold:
                        await message.reply(dont_forget_to_clear_text, parse_mode="Markdown")
                    update_messages(message.chat.id, "assistant", response[1])
                else:
                    if response[1] == "APIError":
                        await message.reply(errors_response_texts(response[1]), parse_mode="Markdown")
                    elif response[1] == "RateLimitError":
                        await message.reply(errors_response_texts(response[1]), parse_mode="Markdown")
                    elif response[1] == "InvalidRequestError":
                        await message.reply(errors_response_texts(response[1]), parse_mode="Markdown")
                        delete_record(message.chat.id)
                    else:
                        await message.reply(unknown_error_response_text, parse_mode="Markdown")
                        delete_record(message.chat.id)
        else:
            await message.reply(admins_balance_low_text, parse_mode="Markdown")
    else:
        await message.reply(work_in_public_chat_error, parse_mode="Markdown")


# Menu

@dp.callback_query_handler(text="help")
async def help_pressed(call: types.CallbackQuery):
    await call.message.edit_text(help_text, parse_mode="Markdown", reply_markup=go_to_main_menu())


@dp.callback_query_handler(text="settings")
async def settings_pressed(call: types.CallbackQuery):
    users_temperature = get_from_user(call.from_user.id, "temperature")
    frequency_penalty = get_from_user(call.from_user.id, "frequency_penalty")
    presence_penalty = get_from_user(call.from_user.id, "presence_penalty")
    await call.message.edit_text(settings_text(users_temperature, frequency_penalty, presence_penalty),
                                 parse_mode="Markdown",
                                 reply_markup=choose_parameter_keyboard(users_temperature,
                                                                        frequency_penalty,
                                                                        presence_penalty))


class TopUp(StatesGroup):
    top_up_amount = State()


@dp.callback_query_handler(text="top_up")
async def top_up_started(call: types.CallbackQuery):
    await call.message.edit_text(how_much_to_top_up_text)
    await TopUp.top_up_amount.set()


@dp.message_handler(state=TopUp.top_up_amount)
async def top_up_progress(message: types.Message, state: FSMContext):
    if message.text != "/start" and message.text != "/clear" and message.text.isdigit():
        async with state.proxy() as top_up_data:
            top_up_data['top_up_amount'] = message.text
        exchanged_tokens = exchange_rate_converter(int(top_up_data['top_up_amount']))
        await message.answer(f"Пополняем на {top_up_data['top_up_amount']} рублей? Это {exchanged_tokens} токенов.",
                             reply_markup=buy_keyboard(top_up_data['top_up_amount']))
        await state.finish()
    else:
        await message.answer(input_error, reply_markup=go_to_main_menu())
        await state.finish()


# Payments

@dp.callback_query_handler(lambda c: c.data.startswith('buy'))
async def proceed_to_intro_pressed(call: types.CallbackQuery):
    price = int(call.data.split("&")[1])
    await bot.send_invoice(call.from_user.id,
                           title='Пополнение аккаунта',
                           description="Покупка токенов для сервиса.",
                           provider_token=payments_provider_token,
                           need_email=True,
                           send_email_to_provider=True,
                           # provider_data=make_providers_data(price),
                           currency='rub',
                           photo_url=invoice_img,
                           photo_height=512,  # !=0/None or picture won't be shown
                           photo_width=512,
                           is_flexible=False,  # True If you need to set up Shipping Fee
                           prices=make_prices(price),
                           start_parameter='time-machine-example',
                           protect_content=True,
                           payload=f"{price}")


@dp.shipping_query_handler(lambda query: True)
async def shipping(shipping_query: types.ShippingQuery):
    await bot.answer_shipping_query(shipping_query.id, ok=True, shipping_options=shipping_options,
                                    error_message=payment_error)


@dp.pre_checkout_query_handler(lambda query: True)
async def checkout(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                        error_message=payment_error)


@dp.message_handler(content_types=ContentTypes.SUCCESSFUL_PAYMENT)
async def got_payment(message: types.Message):
    income = int(message.successful_payment.invoice_payload)
    increase_users_balance(message.from_user.id, exchange_rate_converter(income))
    await bot.send_message(message.from_user.id, f"Покупка успешна. Зачислено {income} "
                                                 f"рублей или {exchange_rate_converter(income)} "
                                                 f"токенов.", reply_markup=go_to_main_menu())


@dp.callback_query_handler(lambda c: c.data.startswith("edit_parameter"))
async def beforefork_called(call: types.CallbackQuery):
    splitted = call.data.split("&")
    parameter = splitted[2]
    value = float(splitted[3])
    action = splitted[1]
    if action != "regular":
        new_values_list = get_next_value_and_action(action, value, parameter)
        value = new_values_list[0]
        action = new_values_list[1]
    await call.message.edit_text(f"{parameters_meanings[parameter]}: {value}",
                                 reply_markup=edit_parameter_keyboard(parameter, action, value))


@dp.callback_query_handler(lambda c: c.data.startswith("set_parameter"))
async def beforefork_called(call: types.CallbackQuery):
    splitted = call.data.split("&")
    parameter_to_update = splitted[1]
    value_to_update = splitted[2]
    update_user(call.from_user.id, parameter_to_update, value_to_update)
    await call.message.edit_text(f"Записал {parameters_meanings[parameter_to_update]}: {value_to_update}",
                                 reply_markup=parameter_update_done_keyboard())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)
