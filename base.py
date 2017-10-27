REAL_TOKEN = "454168022:AAENNH29QY7oBnMQAN6Pd1mJjUNeoGKizT8"
TOKEN = "472298128:AAHjJOgBElcCZfyv-VIpSP0khOXsZuvRHsU"

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
						  ConversationHandler)

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)

logger = logging.getLogger(__name__)

GENDER, LOCATION, WHATUWANT = range(3)


def start(bot, update):
	reply_keyboard = [['Boy', 'Girl', 'Other']]

	update.message.reply_text(
		'Hi! My name is Professor Bot. I will hold a conversation with you. '
		'Send /cancel to stop talking to me.\n\n'
		'Are you a boy or a girl?',
		reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

	return GENDER


def gender(bot, update):
	user = update.message.from_user
	logger.info("Gender of %s: %s", user.first_name, update.message.text)
	update.message.reply_text('Gorgeous! Now, send me your location please, '
							  'or send /skip if you don\'t want to.',
							  reply_markup=ReplyKeyboardRemove())

	return LOCATION


def location(bot, update):
	reply_keyboard = [['Run', 'Swim', 'Walk', 'Die']]

	user = update.message.from_user
	user_location = update.message.location
	print(user_location)
	logger.info("Location of %s: %f / %f", user.first_name, user_location.latitude,
				user_location.longitude)
	update.message.reply_text('Maybe I can visit you sometime! '
							  'What do you feel like doing today?',
							  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

	return WHATUWANT


def skip_location(bot, update):
	user = update.message.from_user
	logger.info("User %s did not send a location.", user.first_name)
	update.message.reply_text('You seem a bit paranoid! '
							  'What do you feel like doing today?',
							  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

	return WHATUWANT


def whatuwant(bot, update):
	user = update.message.from_user
	logger.info("%s wants to : %s", user.first_name, update.message.text)
	update.message.reply_text('Thank you! I hope we can talk again some day.',
							  reply_markup=ReplyKeyboardRemove())

	return ConversationHandler.END


def cancel(bot, update):
	user = update.message.from_user
	logger.info("User %s canceled the conversation.", user.first_name)
	update.message.reply_text('Bye! I hope we can talk again some day.',
							  reply_markup=ReplyKeyboardRemove())

	return ConversationHandler.END


def error(bot, update, error):
	"""Log Errors caused by Updates."""
	logger.warning('Update "%s" caused error "%s"', update, error)


def main():
	# Create the EventHandler and pass it your bot's token.
	updater = Updater(TOKEN)

	# Get the dispatcher to register handlers
	dp = updater.dispatcher

	# Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
	conv_handler = ConversationHandler(
		entry_points=[CommandHandler('start', start)],

		states={
			GENDER: [RegexHandler('^(Boy|Girl|Other)$', gender)],

			LOCATION: [MessageHandler(Filters.location, location),
					   CommandHandler('skip', skip_location)],

			WHATUWANT: [MessageHandler(Filters.text, whatuwant)]
		},

		fallbacks=[CommandHandler('cancel', cancel)]
	)

	dp.add_handler(conv_handler)

	# log all errors
	dp.add_error_handler(error)

	# Start the Bot
	updater.start_polling()

	# Run the bot until you press Ctrl-C or the process receives SIGINT,
	# SIGTERM or SIGABRT. This should be used most of the time, since
	# start_polling() is non-blocking and will stop the bot gracefully.
	updater.idle()


if __name__ == '__main__':
	main()