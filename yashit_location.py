TOKEN = "454168022:AAENNH29QY7oBnMQAN6Pd1mJjUNeoGKizT8"
DISTANCE_THRESHOLD = 5

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
						  ConversationHandler)
import gpxpy.geo
import logging

from math import radians, cos, sin, asin, sqrt

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)

logger = logging.getLogger(__name__)

GENDER, PHOTO, LOCATION, BIO = range(4)


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
	update.message.reply_text('Now, send me your location please, '
							  'or send /skip if you don\'t want to.',
							  reply_markup=ReplyKeyboardRemove())
	return LOCATION


def location(bot, update):
	user = update.message.from_user
	user_location = update.message.location

	logger.info("Location of %s: %f / %f", user.first_name, user_location.latitude,
				user_location.longitude)
	update.message.reply_text('Maybe I can visit you sometime! '
							  'At last, tell me something about yourself.')
	return BIO


def skip_location(bot, update):
	user = update.message.from_user
	logger.info("User %s did not send a location.", user.first_name)
	update.message.reply_text('You seem a bit paranoid! '
							  'At last, tell me something about yourself.')

	return BIO

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
	# {258937187: {'first_name': 'Deepak', 'username': 'dvatsav', 'coordinates': (28.690764, 77.214089), 'activity': 'Gym'}}



def bio(bot, update):
	user = update.message.from_user
	logger.info("Bio of %s: %s", user.first_name, update.message.text)
	update.message.reply_text('Thank you! I hope we can talk again some day.')

	return ConversationHandler.END

def checkDistance(user_location, other_user_location):
	user_lon = user_location["longitude"]
	user_lat = user_location["latitude"]
	other_lon = other_user_location["longitude"]
	other_lat = other_user_location["latitude"]

	lon1, lat1, lon2, lat2 = map(radians, [user_lon, user_lat, other_lon, other_lat])
 
	km = 6371*(2*asin(sqrt(sin((lat2 - lat1)/2)**2 + cos(lat1) * cos(lat2) * sin((lon2 - lon1)/2)**2)))
	print ("The distance between the two points is: " + str(km))
	return km

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
	updater = Updater(TOKEN)

	dp = updater.dispatcher
	conv_handler = ConversationHandler(
		entry_points=[CommandHandler('start', start)],

		states={
			GENDER: [RegexHandler('^(Boy|Girl|Other)$', gender)],

			LOCATION: [MessageHandler(Filters.location, location),
					   CommandHandler('skip', skip_location)],

			BIO: [MessageHandler(Filters.text, bio)]
		},

		fallbacks=[CommandHandler('cancel', cancel)]
	)

	dp.add_handler(conv_handler)
	dp.add_error_handler(error)
	updater.start_polling()
	updater.idle()


if __name__ == '__main__':
	main()