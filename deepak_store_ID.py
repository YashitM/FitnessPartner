TOKEN = "439442918:AAFtoa3vmZ9uvBc3eNYojEVXXGm2GkTYmAE"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
						  ConversationHandler)
import requests
import json
import pickle
import logging
from math import radians, cos, sin, asin, sqrt
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)

logger = logging.getLogger(__name__)

LOCATION, BIO = range(2)
DISTANCE_THRESHOLD = 5
database = {}

def find_partner(user_location, user_chat_id):
	try:
		partner_list = []
		current_user_dictionary = database
		# read dictionary from pickle
		for i in current_user_dictionary:
			if i != user_chat_id:
				print (i, user_chat_id)
				coordinate_dictionary = {}
				inner_dictionary = current_user_dictionary[i]
				coordinates = inner_dictionary['coordinates']
				coordinate_dictionary["longitude"] = coordinates[1]
				coordinate_dictionary["latitude"] = coordinates[0]
				if checkDistance(user_location, coordinate_dictionary) < DISTANCE_THRESHOLD:
					partner_list.append(inner_dictionary)

		print ("list is: ", partner_list)
	except:
		print ("list is empty")
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
	print (update.message.chat.id)
	print (update.message.chat.first_name)
	database[update.message.chat.id] = {}
	update.message.reply_text('I see! Please send me your location, '
							  'so I know where you live, or send /skip if you don\'t want to.',
							  reply_markup=ReplyKeyboardRemove())

	return LOCATION




def location(bot, update):
	user = update.message.from_user
	user_location = update.message.location
	reply_keyboard = [['Running', 'Swimming', 'Gym']]
	logger.info("Location of %s: %f / %f", user.first_name, user_location.latitude,
				user_location.longitude)
	database[update.message.chat.id]['first_name'] = user.first_name
	database[update.message.chat.id]['username'] = user.username
	database[update.message.chat.id]['coordinates'] = (user_location.latitude, user_location.longitude)
	find_partner(user_location, update.message.chat.id)
	update.message.reply_text('Maybe I can visit you sometime! '
							  'At last, What sort of activity interests you?', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

	return BIO


def skip_location(bot, update):
	user = update.message.from_user
	logger.info("User %s did not send a location.", user.first_name)
	update.message.reply_text('You seem a bit paranoid! '
							  'At last, tell me something about yourself.')

	return BIO


def bio(bot, update):
	database[update.message.chat.id]['activity'] = update.message.text
	with open('database.pickle', 'wb') as f:
		pickle.dump(database, f)
	user = update.message.from_user
	logger.info("Bio of %s: %s", user.first_name, update.message.text)
	update.message.reply_text('Thank you! I hope we can talk again some day.')
	print (database)
	
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

			BIO: [MessageHandler(Filters.text, bio)]

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
	try:
		database = pickle.load(open("database.pickle", 'rb'))
		print (database)
	except:
		database = {}
	main()

