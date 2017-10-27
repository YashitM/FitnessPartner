REAL_TOKEN = "454168022:AAENNH29QY7oBnMQAN6Pd1mJjUNeoGKizT8"
TOKEN = "472298128:AAHjJOgBElcCZfyv-VIpSP0khOXsZuvRHsU"

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
						  ConversationHandler)
from math import radians, cos, sin, asin, sqrt
DISTANCE_THRESHOLD = 5

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)

logger = logging.getLogger(__name__)

LOCATION, WHATUWANT = range(2)




def find_partner(user_location, user_chat_id):
	partner_list = []
	current_user_dictionary = {}
	# read dictionary from pickle
	for i in current_user_dictionary:
		if i != user_chat_id:
			coordinate_dictionary = {}
			inner_dictionary = current_user_dictionary[i]
			coordinates = inner_dictionary['coordinates']
			coordinate_dictionary["longitude"] = coordinates[1]
			coordinate_dictionary["latitude"] = coordinates[0]
			if checkDistance(user_location,coordinate_dictionary) < DISTANCE_THRESHOLD:
				partner_list.append(inner_dictionary)
	return partner_list

def checkDistance(user_location, other_user_location):
	user_lon = user_location["longitude"]
	user_lat = user_location["latitude"]
	other_lon = other_user_location["longitude"]
	other_lat = other_user_location["latitude"]

	lon1, lat1, lon2, lat2 = map(radians, [user_lon, user_lat, other_lon, other_lat])

	km = 6371*(2*asin(sqrt(sin((lat2 - lat1)/2)**2 + cos(lat1) * cos(lat2) * sin((lon2 - lon1)/2)**2)))
	print ("The distance between the two points is: " + str(km))
	return km

def start(bot, update):
	update.message.reply_text(
		'Hi! My name is Fitness Bot.'
		'Send /cancel to stop talking to me.\n\n'
		'Before we get started I\'ll need your location to start with.')

	return LOCATION


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
	logger.info("Location of %s: %f / %f", user.first_name, user_location.latitude,
				user_location.longitude)
	update.message.reply_text('Maybe I can visit you sometime! '
							  'What do you feel like doing today?',
							  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

	return WHATUWANT


def skip_location(bot, update):
	reply_keyboard = [['Run', 'Swim', 'Walk', 'Die']]

	user = update.message.from_user
	logger.info("User %s did not send a location.", user.first_name)
	update.message.reply_text('You seem a bit paranoid! '
							  'What do you feel like doing today?',
							  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

	return WHATUWANT


def whatuwant(bot, update):
	user = update.message.from_user
	logger.info("%s wants to : %s", user.first_name, update.message.text)
	update.message.reply_text('Ok looking for nearby users that want to ' + update.message.text,
							  reply_markup=ReplyKeyboardRemove())

	#Todo call function to get nearby user should return user's username or list of username(s)
	# usernameList = ["This_is_username1", "This_is_username2", "This_is_username3"]
	usernameList = find_partner()
	update.message.reply_text('Found the following user(s) near you with similar interest.\n')

	for data in usernameList:
		update.message.reply_text('http://t.me/' + data['username'] + '/')


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