import logging
import re
import paramiko

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

TOKEN = "7013840002:AAFQNM5VH--lY8uFStOpIzrbZcU1dDNifGU"

SSH_HOST = '192.168.146.157'
SSH_PORT = 22
SSH_USERNAME = 'kali'
SSH_PASSWORD = 'kali'

# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def execute_ssh_command(command):
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=SSH_HOST, port=SSH_PORT, username=SSH_USERNAME, password=SSH_PASSWORD)
        stdin, stdout, stderr = ssh_client.exec_command(command)
        output = stdout.read() + stderr.read()
        ssh_client.close()
        output = str(output).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
        return output
    except paramiko.SSHException as e:
        logger.error(f"SSH error: {e}")
        return "An SSH error occurred."
    except Exception as e:
        logger.error(f"Error executing SSH command: {e}")
        return "An error occurred while executing the command."


def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')


def helpCommand(update: Update, context):
    update.message.reply_text('Help!')

def getRelease(update: Update, context):
    release_info = execute_ssh_command('lsb_release -a')
    update.message.reply_text(release_info)

def getUname(update: Update, context):
    uname_info = execute_ssh_command('uname -a')
    update.message.reply_text(uname_info)

def getUptime(update: Update, context):
    uptime_info = execute_ssh_command('uptime')
    update.message.reply_text(uptime_info)

def getDf(update: Update, context):
    df_info = execute_ssh_command('df -h')
    update.message.reply_text(df_info)

def getFree(update: Update, context):
    free_info = execute_ssh_command('free -m')
    update.message.reply_text(free_info)

def getMpstat(update: Update, context):
    mpstat_info = execute_ssh_command('mpstat')
    update.message.reply_text(mpstat_info)

def getW(update: Update, context):
    w_info = execute_ssh_command('w')
    update.message.reply_text(w_info)

def getAuths(update: Update, context):
    auths_info = execute_ssh_command('last -10')
    update.message.reply_text(auths_info)

def getCritical(update: Update, context):
    critical_info = execute_ssh_command('grep "CRITICAL" /var/log/log.log -m 5')
    update.message.reply_text(critical_info)

def getPs(update: Update, context):
    ps_info = execute_ssh_command('ps')
    update.message.reply_text(ps_info)

def getSs(update: Update, context):
    ss_info = execute_ssh_command('ss -tuln')
    update.message.reply_text(ss_info)

def getAptList(update: Update, context):
    if context.args:
        package_name = ' '.join(context.args)
        apt_list_info = execute_ssh_command(f'apt show {package_name}')
        update.message.reply_text(apt_list_info)
    else:
        apt_list_info = execute_ssh_command('apt list --installed')
        apt_list_lines = apt_list_info.split('\n')
        for i in range(0, len(apt_list_lines), 20):
            update.message.reply_text('\n'.join(apt_list_lines[i:i + 20]))

def getServices(update: Update, context):
    if context.args:
        service_name = ' '.join(context.args)
        services_info = execute_ssh_command(f'service {service_name} status')
        update.message.reply_text(services_info)
    else:
        services_info = execute_ssh_command('service --status-all')
        update.message.reply_text(services_info)

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
    user_input = update.message.text

    emailRegex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

    emailList = emailRegex.findall(user_input)

    if not emailList:
        update.message.reply_text('Адреса электронной почты не найдены')
        return

    emails = ''
    for i, email in enumerate(emailList):
        emails += f'{i + 1}. {email}\n'

    update.message.reply_text(emails)
    return ConversationHandler.END

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
    dp.add_handler(CommandHandler("get_release", getRelease))
    dp.add_handler(CommandHandler("get_uname", getUname))
    dp.add_handler(CommandHandler("get_uptime", getUptime))
    dp.add_handler(CommandHandler("get_df", getDf))
    dp.add_handler(CommandHandler("get_free", getFree))
    dp.add_handler(CommandHandler("get_mpstat", getMpstat))
    dp.add_handler(CommandHandler("get_w", getW))
    dp.add_handler(CommandHandler("get_auths", getAuths))
    dp.add_handler(CommandHandler("get_critical", getCritical))
    dp.add_handler(CommandHandler("get_ps", getPs))
    dp.add_handler(CommandHandler("get_ss", getSs))
    dp.add_handler(CommandHandler("get_apt_list", getAptList))
    dp.add_handler(CommandHandler("get_services", getServices))

    # Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Запускаем бота
    updater.start_polling()

    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
