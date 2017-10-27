TOKEN = "439442918:AAFtoa3vmZ9uvBc3eNYojEVXXGm2GkTYmAE"

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler)
import pickle
import logging

reminders = {}

QUESTION1, QUESTION2 = range(2)

def schedule(bot, update):
	update.message.reply_text("welcome to the scheduling section. I'll need you to answer a few questions, "
		"What would you like to be reminded off?")
	return QUESTION1

def question1(bot, update):
	reminders[update.message.chat.id]['Reminder text'] = update.message.text
	update.message.reply_text("what time would you like to be reminded everyday? please enter 24 hour format (eg 1700)")
	return QUESTION2

def question2(bot, update):
	reminders[update.message.chat.id]['Reminder time'] = update.message.text
	with open('reminders.pickle', 'wb') as f:
		pickle.dump(reminders, f)
	update.message.reply_text("okay, saved")
	return ConversationHandler.END

def error(bot, update, error):
	logger.warning('Update "%s" caused error "%s"', update, error)

def main():
	updater = Updater(TOKEN)
	dp = updater.dispatcher
	conv_handler = ConversationHandler(
		entry_points=[CommandHandler('schedule', start)],
		states={
			QUESTION1: [MessageHandler(Filters.text, question1)],
			QUESTION2: [MessageHandler(Filters.text, question2)]
		},
		fallbacks=[CommandHandler('cancel', cancel)]
	)
	dp.add_handler(conv_handler)
	dp.add_error_handler(error)
	updater.start_polling()
	updater.idle()


if __name__ == '__main__':
	try:
		reminders = pickle.load(open("reminders.pickle", 'rb'))
	except:
		reminders = {}
	main()