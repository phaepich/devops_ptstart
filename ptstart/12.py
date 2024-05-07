import logging
import re
import paramiko

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

TOKEN = "7013840002:AAFQNM5VH--lY8uFStOpIzrbZcU1dDNifGU"

# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')


def helpCommand(update: Update, context):
    update.message.reply_text('Help!')


def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')

    return 'findPhoneNumbers'


def findPhoneNumbers(update: Update, context):
    user_input = update.message.text  # Получаем текст, содержащий(или нет) номера телефонов

    phoneNumRegex = re.compile(r'(?:\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}')

    phoneNumberList = phoneNumRegex.findall(user_input)  # Ищем номера телефонов

    if not phoneNumberList:  # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return  # Завершаем выполнение функции

    phoneNumbers = ''  # Создаем строку, в которую будем записывать номера телефонов
    for i, number in enumerate(phoneNumberList):
        phoneNumbers += f'{i + 1}. {number}\n'  # Записываем очередной номер

    update.message.reply_text(phoneNumbers)  # Отправляем сообщение пользователю
    return ConversationHandler.END  # Завершаем работу обработчика диалога

def findEmailsCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска адресов электронной почты: ')

    return 'findEmails'

def findEmails(update: Update, context):
    user_input = update.message.text  # Получаем текст, содержащий(или нет) адреса электронной почты

    # Регулярное выражение для поиска адресов электронной почты
    emailRegex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

    emailList = emailRegex.findall(user_input)  # Ищем адреса электронной почты

    if not emailList:  # Обрабатываем случай, когда адресов электронной почты нет
        update.message.reply_text('Адреса электронной почты не найдены')
        return  # Завершаем выполнение функции

    emails = ''  # Создаем строку, в которую будем записывать адреса электронной почты
    for i, email in enumerate(emailList):
        emails += f'{i + 1}. {email}\n'  # Записываем очередной адрес

    update.message.reply_text(emails)  # Отправляем сообщение пользователю
    return ConversationHandler.END  # Завершаем работу обработчика диалога

def verifyPasswordCommand(update: Update, context):
    update.message.reply_text('Введите пароль для проверки сложности: ')

    return 'verifyPassword'


def verifyPassword(update: Update, context):
    user_input = update.message.text

    passwordRegex = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()])[A-Za-z\d!@#$%^&*()]{8,}$')

    if passwordRegex.match(user_input):
        update.message.reply_text('Пароль сложный')
    else:
        update.message.reply_text('Пароль простой')

    return ConversationHandler.END  # Завершаем работу обработчика диалога

def echo(update: Update, context):
    update.message.reply_text(update.message.text)


def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик диалога
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'find_phone_number': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
        },
        fallbacks=[]
    )

    convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailsCommand)],
        states={
            'findEmails': [MessageHandler(Filters.text & ~Filters.command, findEmails)],
        },
        fallbacks=[]
    )

    convHandlerVerifyPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verifyPasswordCommand)],
        states={
            'verifyPassword': [MessageHandler(Filters.text & ~Filters.command, verifyPassword)],
        },
        fallbacks=[]
    )

    # Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmails)
    dp.add_handler(convHandlerVerifyPassword)

    # Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Запускаем бота
    updater.start_polling()

    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
