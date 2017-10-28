import telebot
import sys
from config import token, log_name
import logging
bot = telebot.TeleBot(token)
logger = logging.getLogger(log_name)
logging.basicConfig(filename=log_name + '.log',
                    format='[%(asctime)s] SENDER %(levelname)s - %(message)s',
                    datefmt='%d.%m.%Y %H:%M:%S')
logger.setLevel(logging.INFO)
try:
    bot.send_message(int(sys.argv[1]), (sys.argv[2]))
    logger.info('Successfully sent message!')
except Exception as ex:
    logger.error('Failed to send message: {0!s}'.format(str(ex)))