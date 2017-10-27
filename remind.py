TOKEN = "439442918:AAFtoa3vmZ9uvBc3eNYojEVXXGm2GkTYmAE"

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler)
import pickle
import logging
import time

reminders = {}
def main():
	prevtime = time.time()
	while True:
		if time.time() - prevtime >= 60:
			try:
				reminders = pickle.load(open("reminders.pickle", 'rb'))
			except:
				reminders = {}
		for _ in reminders:
			if time.ctime()[11:13] + time.ctime()[14:16] == reminders[_]['Reminder time']:
				_.send


if __name__ == '__main__':
	main()