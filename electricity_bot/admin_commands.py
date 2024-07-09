from telebot import types, TeleBot, apihelper  # type: ignore

from electricity_bot.vars import (
    cancel,
    schedules_markup,
    generic_choice,
    admin_markup,
    group_choice,
    stats_group_str,
    outages_group_str,
)
from electricity_bot.time import get_date, get_time
from electricity_bot.logger import log_cmd

import logging

logger = logging.getLogger(__name__)


def not_admin(message: types.Message, bot: TeleBot) -> None:
    logger.info(
        f'{message.from_user.first_name} {message.from_user.last_name} [{message.from_user.id}] has used the following command: "not_admin"'
    )
    bot.send_message(
        message.from_user.id,
        f" \n\n❌ Ви не є адміном цього бота.",
        parse_mode="html",
    )


def menu(message: types.Message, bot: TeleBot) -> None:
    logger.info(
        f'{message.from_user.first_name} {message.from_user.last_name} [{message.from_user.id}] has used the following command: "admin_menu"'
    )
    bot.send_message(
        message.from_user.id,
        f"💻 Оберіть одну з опцій.",
        parse_mode="html",
        reply_markup=admin_markup,
    )


def _blacklist_(message: types.Message, bot: TeleBot) -> None:
    logger.info(
        f'{message.from_user.first_name} {message.from_user.last_name} [{message.from_user.id}] has used the following command: "blacklist 1"'
    )
    bot.send_message(
        message.from_user.id,
        f"🤖 Введіть номер або User ID користувача, якого ви хочете заблокувати.",
        parse_mode="html",
        reply_markup=cancel,
    )
    bot.register_next_step_handler(message, _blacklist, bot)


def _blacklist(message: types.Message, bot: TeleBot) -> None:
    log_cmd(message, "blacklist 2")
    try:
        if message.text[0] == "+":
            number = message.text
        else:
            number = int(message.text)
        bot.send_message(
            message.from_user.id,
            f"❌ Напишіть причину блокування:",
            parse_mode="html",
            reply_markup=cancel,
        )
        bot.register_next_step_handler(message, blacklist, bot, number)
    except:
        bot.send_message(
            message.from_user.id,
            f"❌ {number} не є коректним номером або Telegram ID",
            parse_mode="html",
            reply_markup=cancel,
        )
        bot.register_next_step_handler(message, _blacklist, bot)


def blacklist(message: types.Message, bot: TeleBot, number: int | str) -> None:
    log_cmd(message, "blacklist 3")
    bot.user_storage.blacklist(number, message.text)
    logger.info(
        f"Admin {message.from_user.first_name} {message.from_user.last_name} [{message.from_user.id}] blocked {number}, reason: {message.text}"
    )
    logger.info(
        f"Admin {message.from_user.first_name} {message.from_user.last_name} [{message.from_user.id}] blocked {number}, reason: {message.text}"
    )
    bot.send_message(
        message.from_user.id,
        f"✅ Успішно заблоковано {number}",
        parse_mode="html",
        reply_markup=admin_markup,
    )


def _unblacklist(message: types.Message, bot: TeleBot) -> None:
    log_cmd(message, "unblacklist 1")
    bot.send_message(
        message.from_user.id,
        f"🤖 Введіть номер або User ID користувача, якого ви хочете розблокувати.",
        parse_mode="html",
        reply_markup=cancel,
    )
    bot.register_next_step_handler(message, unblacklist, bot)


def unblacklist(message: types.Message, bot: TeleBot) -> None:
    log_cmd(message, "unblacklist 2")
    number = message.text
    if bot.user_storage.unblacklist(number):
        bot.send_message(
            message.from_user.id,
            f"✅ Успішно розблоковано {number}",
            parse_mode="html",
            reply_markup=admin_markup,
        )
    else:
        bot.send_message(
            message.from_user.id,
            f"❌ {number} не є заблокованим.",
            parse_mode="html",
            reply_markup=admin_markup,
        )


def current_date(message: types.Message, bot: TeleBot) -> None:
    bot.send_message(
        message.from_user.id,
        f"📅 Сьогоднішня дата: {get_date()} {get_time()}",
        parse_mode="html",
        reply_markup=admin_markup,
    )


def add_schedule(
    message: types.Message,
    bot: TeleBot,
) -> None:
    log_cmd(message, "add_schedule")
    markup = schedules_markup(bot)
    bot.send_message(
        message.from_user.id,
        f"Оберіть дату.",
        parse_mode="html",
        reply_markup=markup,
    )
    bot.register_next_step_handler(message, _add_schedule, bot)


def _add_schedule(
    message: types.Message,
    bot: TeleBot,
) -> None:
    if message.text == "Назад":
        menu(message, bot)
    else:
        if bot.id_storage.exists(message.text):
            bot.send_message(
                message.from_user.id,
                f"🤖 Цей графік вже було додано. Оновити його?",
                parse_mode="html",
                reply_markup=generic_choice,
            )
            bot.register_next_step_handler(
                message, do_update_schedule, bot, message.text
            )
        else:
            bot.send_message(
                message.from_user.id,
                f"🤖 Надішліть фотографію графіку.",
                parse_mode="html",
                reply_markup=cancel,
            )
            bot.register_next_step_handler(message, handle_photos, bot, message.text)


def do_update_schedule(message: types.Message, bot: TeleBot, date: None) -> None:
    if message.text == "Назад" or message.text == "Ні":
        menu(message, bot)
    elif message.text == "Так":
        bot.send_message(
            message.from_user.id,
            f"🛠 Надішліть фотографію графіку.",
            parse_mode="html",
            reply_markup=cancel,
        )
        bot.register_next_step_handler(message, handle_photos, bot, date)
    else:
        bot.send_message(
            message.from_user.id,
            f'🤖 Не розумію. Оберіть відповідь "Так", "Ні" або "Назад".',
            parse_mode="html",
            reply_markup=generic_choice,
        )
        bot.register_next_step_handler(message, do_update_schedule, bot, message.text)


def handle_photos(
    message: types.Message,
    bot: TeleBot,
    date: str = None,
) -> None:
    if date == None:
        date = get_date()
    log_cmd(message, "handle_photos")
    if message.content_type == "photo":
        file_id = message.photo[-1].file_id
        bot.id_storage.save(file_id, date)

        bot.send_message(
            message.from_user.id,
            f"✅ Графік успішно додано.",
            parse_mode="html",
            reply_markup=admin_markup,
        )
        menu(message, bot)
    else:
        if message.text == "Назад":
            menu(message, bot)
        else:
            bot.send_message(
                message.from_user.id,
                f"🤖 Надішліть коректну фотографію.",
                parse_mode="html",
                reply_markup=cancel,
            )
            bot.register_next_step_handler(message, handle_photos, bot)


def _announce_(message: types.Message, bot: TeleBot) -> None:
    log_cmd(message, "announce 1")
    bot.send_message(
        message.from_user.id,
        f"📲 Оберіть групу користувачів, для яких ви хочете створити оголошення.",
        parse_mode="html",
        reply_markup=group_choice,
    )
    bot.register_next_step_handler(message, _announce, bot)


def _announce(message: types.Message, bot: TeleBot):
    log_cmd(message, "announce 2")
    if message.text == "Назад":
        menu(message, bot)
    elif message.text == outages_group_str or message.text == stats_group_str:
        if message.text == outages_group_str:
            group = "outages"
        else:
            group = "stats"
        bot.send_message(
            message.from_user.id,
            f"⌨️ Тепер напишіть ваше оголошення.",
            parse_mode="html",
            reply_markup=cancel,
        )
        bot.register_next_step_handler(message, announce, bot, group)
    else:
        bot.send_message(
            message.from_user.id,
            f'🤖 Не розумію. Оберіть відповідь "{outages_group_str}", "{stats_group_str}" або "Назад".',
            parse_mode="html",
            reply_markup=generic_choice,
        )
        bot.register_next_step_handler(message, _announce, bot, group)


def announce(message: types.Message, bot: TeleBot, group: str):
    log_cmd(message, "announce 3")
    if message.text == "Назад":
        menu(message, bot)
    else:
        logger.info(
            f'Admin {message.from_user.first_name} {message.from_user.last_name} [{message.from_user.id}] announced to "{group}", text: {message.text}'
        )
        logger.info(
            f'Admin {message.from_user.first_name} {message.from_user.last_name} [{message.from_user.id}] announced to "{group}", text: {message.text}'
        )
        for user_id in bot.user_storage.read()[group]:
            try:
                bot.send_message(
                    user_id,
                    f"⚠️ Оголошення від адміністратора:\n\n{message.text}",
                    parse_mode="html",
                )
                logger.info(f"Notified {user_id}")
            except apihelper.ApiTelegramException as e:
                if e.error_code == 403:
                    logger.error(
                        f"{user_id} has blocked the bot. Removing them from the list"
                    )
                    bot.user_storage.delete(user_id, group)
                elif e.error_code in [401, 404]:
                    logger.error(
                        f"Could not access {user_id}. Removing them from the list"
                    )
                    bot.user_storage.delete(user_id, group)
                continue
            except Exception as e:
                logger.error(
                    f"{e} occured. Take actions regarding this error as soon as possible."
                )
                continue

        logger.info(f"Notified users")
        bot.send_message(
            message.from_user.id,
            f"✅ {len(bot.user_storage.read()[group])} отримали ваше оголошення.",
            parse_mode="html",
            reply_markup=admin_markup,
        )

        menu(message, bot)
