import asyncio
import datetime

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ReplyKeyboardRemove
from aiogram.types import Message, ContentType
from aiogram.types import PreCheckoutQuery, LabeledPrice

from disp import dp, pay_token, bot
from functions.DB.cart import current_cart_id, add_info_to_cart, data_invoice_creating, clear_user_cart_data, \
    total_sum_counter, get_last_id
from functions.DB.current_orders import add_info_to_current_orders_from_sheet, current_order_number
from functions.DB.current_orders import orders_in_work_amount
from functions.DB.paid_db import add_info_to_paid_data
from functions.DB.users_db import insert_bonus, add_new_user, bonuses_amount
from functions.FSM import UserStates
from functions.keyboards.keyboards import points_kbd, menu_btn
from main import logger
from sheets import add_info_to_google_sheet


@dp.message_handler(commands=['start'])
async def send_welcome(message: Message):
    orders_in_work = orders_in_work_amount()
    now = datetime.datetime.now()
    time = now.strftime("%H")

    # Проверка времени работы и кол-ва заказов в минуту
    if orders_in_work > 30:
        await bot.send_message(message.chat.id, "Извините, много заказов, попробуйте снова через несколько минут")
    elif int(time) < 9 or int(time) > 19:
        await bot.send_message(message.chat.id, "Добрый вечер, в данный момент кофейня закрыта")
    else:
        await bot.send_message(message.chat.id,
                               f"Баллы копим или списываем?",
                               reply_markup=points_kbd)
    try:
        await bot.delete_message(message.chat.id, message.message_id - 1)
        await bot.delete_message(message.chat.id, message.message_id - 2)
    except Exception:
        logger.error("Не найден ID сообщения для удаления")
        await bot.send_message(message.chat.id,
                               f"Привет, перед началом заказа выбери:копим баллы или списываем",
                               reply_markup=points_kbd)

    clear_user_cart_data(message.from_user.id)
    add_new_user(message.from_user.id)


@dp.message_handler(commands=['start'], state=[UserStates.points_on, UserStates.points_off])
async def send_welcome_points_on_off(message: Message):
    await bot.delete_message(message.chat.id, message.message_id)


@dp.callback_query_handler()
async def points_action(callback: CallbackQuery):
    orders_in_work = orders_in_work_amount()
    if callback.data == "Yes":
        await UserStates.points_on.set()
        await callback.message.edit_text(
            f"После оплаты заказа баллы будут начислены на ваш счет, пожалуйста, сделайте заказ")
        await bot.send_message(callback.from_user.id, f"Заказов в работе на данный момент: {orders_in_work}",
                               reply_markup=menu_btn)
    elif callback.data == "No":
        await UserStates.points_off.set()
        await callback.message.edit_text("После оформления заказа баллы будут списаны")
        await bot.send_message(callback.from_user.id, f"Заказов в работе на данный момент: {orders_in_work}",
                               reply_markup=menu_btn)


@dp.message_handler(content_types="web_app_data", state=UserStates.points_on)
async def buy_process_state_on(web_app_message, state: FSMContext):
    await state.finish()
    user_id = web_app_message.from_user.id
    web_app_data_dict = eval(web_app_message.web_app_data.data)
    
    # Проверка на "__telegram__themeParams" нужна, так как данные с пк и мобильных устройств разные
    for key in web_app_data_dict:
        if key != "__telegram__themeParams":
            title = key
            size = eval(web_app_data_dict[key]).split()[0]
            syrup = eval(web_app_data_dict[key]).split()[1]
            price = eval(web_app_data_dict[key]).split()[2]
            cart_id = current_cart_id() + 1
            add_info_to_cart(user_id, cart_id, title, size, syrup, price)

    invoice_data = data_invoice_creating(user_id)

    average_price = 0
    try:
        for i in invoice_data:
            average_price += i[5]
    except TypeError:
        logger.error("Произошел сбой в оплате")
        await bot.send_message(web_app_message.chat.id, "Извините, произошел сбой, попробуйте заново")
        await send_welcome(web_app_message)

    bonus_amount = int(average_price * 0.03)

    prices = [LabeledPrice(label=i[2] + " " + i[3] + " " + i[4], amount=i[5] * 100) for i in invoice_data]

    await bot.send_invoice(web_app_message.chat.id,
                           title="BotShop",
                           description=f"Бонусов к начислению: {bonus_amount}",
                           provider_token=pay_token,
                           currency='rub',
                           need_email=False,
                           need_phone_number=False,
                           prices=prices,
                           start_parameter='example',
                           payload='Yes',
                           protect_content=True)

    await bot.send_message(web_app_message.chat.id, "Заказ доступен для оплаты в течение 5 минут",
                           reply_markup=ReplyKeyboardRemove())

    await bot.delete_message(web_app_message.chat.id, web_app_message.message_id)

    try:
        await asyncio.sleep(300)
        await bot.delete_message(web_app_message.chat.id, web_app_message.message_id + 1)
        await bot.delete_message(web_app_message.chat.id, web_app_message.message_id + 2)
    except Exception:
        logger.error("Не найден ID сообщения для удаления")


@dp.message_handler(content_types="web_app_data", state=UserStates.points_off)
async def buy_process_state_off(web_app_message, state: FSMContext):
    await state.finish()

    user_id = web_app_message.from_user.id
    web_app_data_dict = eval(web_app_message.web_app_data.data)

    # Проверка на "__telegram__themeParams" нужна, так как данные с пк и мобильных устройств разные
    for key in web_app_data_dict:
        if key != "__telegram__themeParams":
            title = key
            size = eval(web_app_data_dict[key]).split()[0]
            syrup = eval(web_app_data_dict[key]).split()[1]
            price = eval(web_app_data_dict[key]).split()[2]
            cart_id = current_cart_id() + 1
            add_info_to_cart(user_id, cart_id, title, size, syrup, price)

    invoice_data = data_invoice_creating(user_id)
    total_amount = total_sum_counter(invoice_data)

    # Проверка, что кол-во бонусов не более 30% от суммы заказа
    bonus_amount = bonuses_amount(user_id) if bonuses_amount(user_id) < int(total_amount * 0.3) else int(
        total_amount * 0.3)

    prices = [LabeledPrice(label=i[2] + " " + i[3] + " " + i[4], amount=i[5] * 100) for i in invoice_data]
    prices.append(LabeledPrice(label="Списание баллов", amount=- bonus_amount * 100))

    await bot.send_invoice(web_app_message.chat.id,
                           title="BotShop",
                           description=f"Бонусов к списанию: {bonus_amount}",
                           provider_token=pay_token,
                           currency='rub',
                           need_email=False,
                           need_phone_number=False,
                           prices=prices,
                           start_parameter='example',
                           payload='No ' + str(bonus_amount),
                           protect_content=True)
    await bot.send_message(web_app_message.chat.id, "Заказ доступен для оплаты в течение 5 минут",
                           reply_markup=ReplyKeyboardRemove())

    await bot.delete_message(web_app_message.chat.id, web_app_message.message_id)

    try:
        await asyncio.sleep(300)
        await bot.delete_message(web_app_message.chat.id, web_app_message.message_id + 1)
        await bot.delete_message(web_app_message.chat.id, web_app_message.message_id + 2)
    except Exception:
        logger.error("Не найден ID сообщения для удаления")


@dp.pre_checkout_query_handler(lambda query: True)
async def checkout_process(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: Message):
    bonus_amount = 0
    if message.successful_payment.invoice_payload == "Yes":
        bonus_amount = int(message.successful_payment.total_amount / 100 * 0.03)
    elif message.successful_payment.invoice_payload.split()[0] == "No":
        bonus_amount = - int(message.successful_payment.invoice_payload.split()[1])

    insert_bonus(message.from_user.id, bonus_amount)

    add_info_to_paid_data(message.from_user.id)
    add_info_to_google_sheet(message)
    await add_info_to_current_orders_from_sheet()
    clear_user_cart_data(message.from_user.id)

    order_number = current_order_number(message.from_user.id)

    await bot.send_message(message.chat.id, f'Платеж совершен успешно!\nВаш номер заказа : {order_number}')


@dp.message_handler(lambda message: message.text)
async def wrong_message(message: Message):
    await bot.delete_message(message.chat.id, message.message_id)
