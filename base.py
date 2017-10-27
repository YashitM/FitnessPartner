TOKEN = "454168022:AAENNH29QY7oBnMQAN6Pd1mJjUNeoGKizT8"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
DISTANCE_THRESHOLD = 5

from telegram import Bot
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
						  ConversationHandler)
import pickle
import threading
import logging
import re
import nltk
import time
import requests
import json
from random import randint
from nltk.stem.porter import PorterStemmer
ps = PorterStemmer()
from math import radians, cos, sin, asin, sqrt
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)

logger = logging.getLogger(__name__)

LOCATION, BIO = range(2)

database = {}

# List of facts about health
factList = ['A lack of exercise is now causing as many deaths as smoking across the world, a study suggests.',
			'People who regularly eat dinner or breakfast in restaurants double their risk of becoming obese.',
			'Laughing 100 times is equivalent to 15 minutes of exercise on a stationary bicycle.',
			'Sitting for more than three hours a day can cut two years off a person\'s life expectancy.',
			'Over 30% of cancer could be prevented by avoiding tobacco and alcohol, having a healthy diet and physical activity.',
			'Sleeping less than 7 hours each night reduces your life expectancy.',
			'1 Can of Soda a day increases your chances of getting type 2 diabetes by 22%.',
			'There are more skin cancer cases due to indoor tanning than lung cancer cases due to smoking.',
			'Exercise, like walking, can reduce breast cancer risk by 25%.',
			'McDonalds\' Caesar salad is more fattening than their hamburger. Not like the hamburger isn\'t fattening.',
			'Severe Depression can cause us to biologically age more by increasing the aging process in cells.',
			'Chicken contains 266% more fat than it did 40 years ago. Someone is feeding the chicken a little to much I guess.',
			'Heavy marijuana smokers are at risk for some of the same health effects as cigarette smokers, like bronchitis and other respiratory illnesses.',
			'On average, people who complain live longer. Releasing the tension increases immunity and boosts their health.',
			'A half hour of physical activity 6 days a week is linked to 40% lower risk of early death.',
			'The U.S. spends more money per person on healthcare than any other developed country, yet its life expectancy is below average.',
			'1 out of every 4 dollars employers pay for healthcare in the U.S. is tied to unhealthy lifestyle choices or conditions like smoking, stress, or obesity.',
			'In terms of your health —not how you look or smell— you only really have to shower once or twice a week. Well then I have been doing it right from the past 10 years.',
			'A scientist cracked his knuckles on one hand for over 50 years to prove it did not cause Arthritis. What can I say he was a scientist after all.',
			'Eating too much meat can accelerate your body\'s biological age.',
			'Working past age 65 is linked to longer life, a study found.',
			'People who read books live an average of almost 2 years longer than those who do not read at all, a Yale research found.',
			'You can burn 20% more fat by exercising in the morning on an empty stomach. That is if you get up on time.',
			'Breathing 100% oxygen, instead of the 21% in our atmosphere, is generally bad, and sometimes toxic.',
			'You can tweak your metabolic health by turning down the bedroom thermostat a few degrees.',
			'Violent dreams may be an early sign of brain disorders down the line, including Parkinson\'s disease and dementia. Need to cut short on horror movies I guess.',
			'More than 13 million working days are lost every year because of stress-related illnesses. Stay with me won\'t let you take any stress',
			'A study found that right-handed individuals have better oral hygiene and the lower incidence of caries because of their \
			better manual dexterity and brush efficiency. I knew I was doing something better than the others.',
			'Drinking very hot beverages increases your risk of developing cancer. Need to cut down on that coffee man.',
			'A study showed that it\'s not necessary to run, swim or work out at the gym. Household chores such as vacuuming or scrubbing the floor, \
			or merely walking to work provide enough exercise to protect the heart and extend life. And you though household chores were easy.']
			
def find_partner(user_location, user_chat_id, user_activity):
	try:
		partner_list = []
		current_user_dictionary = database
		for i in current_user_dictionary:
			if i != user_chat_id:
				print (i, user_chat_id)
				coordinate_dictionary = {}
				inner_dictionary = current_user_dictionary[i]
				coordinates = inner_dictionary['coordinates']
				coordinate_dictionary["longitude"] = coordinates[1]
				coordinate_dictionary["latitude"] = coordinates[0]
				if checkDistance(user_location, coordinate_dictionary) < DISTANCE_THRESHOLD and user_activity == inner_dictionary["activity"]:
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
	logger.info("Location of %s: %f / %f", user.first_name, user_location.latitude,
				user_location.longitude)
	database[update.message.chat.id]['first_name'] = user.first_name
	database[update.message.chat.id]['username'] = user.username
	database[update.message.chat.id]['coordinates'] = (user_location.latitude, user_location.longitude)
	#find_partner(user_location, update.message.chat.id)
	update.message.reply_text('Maybe I can visit you sometime! '
							  'At last, What sort of fitness activity interests you?')

	return BIO


def skip_location(bot, update):
	user = update.message.from_user
	logger.info("User %s did not send a location.", user.first_name)
	update.message.reply_text('You seem a bit paranoid! '
							  'I really need your location!')
	return LOCATION


def bio(bot, update):
	message = update.message.text
	database[update.message.chat.id]['activity'] = ps.stem(message)
	with open('database.pickle', 'wb') as f:
		pickle.dump(database, f)
	user = update.message.from_user
	logger.info("Bio of %s: %s", user.first_name, message)
	update.message.reply_text('Finding someone nearby...')
	print (database)
	usernameList = find_partner({"latitude":database[update.message.chat.id]['coordinates'][0], "longitude":database[update.message.chat.id]['coordinates'][1]}, update.message.chat.id, database[update.message.chat.id]['activity'])
	if len(usernameList) != 0:
		update.message.reply_text('Found the following user(s) near you with similar interest.\n')
		for data in usernameList:
			update.message.reply_text('http://t.me/' + data['username'] + '/')
	else:
		update.message.reply_text("No users found with the same interest :( Please try again later!")

	return ConversationHandler.END
	

def cancel(bot, update):
	user = update.message.from_user
	logger.info("User %s canceled the conversation.", user.first_name)
	update.message.reply_text('Bye! I hope we can talk again some day.',
							  reply_markup=ReplyKeyboardRemove())

	return ConversationHandler.END


def error(bot, update, error):
	logger.warning('Update "%s" caused error "%s"', update, error)


def help(bot, update):
	update.message.reply_text('''Hey! Welcome to Fitness Partner. I will help you find a partner for your daily fitness activities to motivate you and keep you going!\n
		You can control me by sending these commands:\n
		1. /start - find a partner for your activity
		2. /setreminder - set a reminder for a particular activity
		3. /showreminders - show all existing reminders
		4. /removereminders - delete reminders
		5. /viewpeople - view what people are upto near you

		
		Miscellaneous Functions: 
		1. /bmicalculator - to calculate your BMI''', reply_markup=ReplyKeyboardRemove())

	return ConversationHandler.END
	

def view_people(bot, update):
	try:
		user_chat_id = update.message.chat.id
		printable_string = ""
		current_user_dictionary = database
		for i in current_user_dictionary:
			if i!=user_chat_id:
				printable_string += "@" + current_user_dictionary[i]["username"] + " is planning to " + current_user_dictionary[i]["activity"] + "!\n" 
		update.message.reply_text(printable_string)
	except:
		print ("list is empty")
	return ConversationHandler.END

def sendToPeople():
	global database
	bot = Bot(token=TOKEN)
	# print ("here", database)
	while True:
		print ("here")
		if (database != {}):
			# print ("here")
			for j in database.keys():
				factNumber = randint(0, len(factList)-1)
				print ("Sending fact number", factNumber, "to user", database[j]["first_name"])
				bot.send_message(chat_id=j, text=factList[factNumber])
		time.sleep(200)
	# threading.Timer(200, sendToPeople).start()

def bmi_calculator(bot, update):
	update.message.reply_text("Enter your height (in m)")
	height = float(update.message.text)
	update.message.reply_text("Enter your weight (in kg)")
	weight = float(update.message.text)
	update.message.reply_text("Your BMI is: " + str(weight/(height)**2))
	
	return ConversationHandler.END

def main():
	updater = Updater(TOKEN)
	dp = updater.dispatcher
	conv_handler = ConversationHandler(
		entry_points=[CommandHandler('start', start), CommandHandler('help',help), CommandHandler('viewpeople',view_people), CommandHandler('bmicalculator',bmi_calculator)],
		states={
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
	try:
		database = pickle.load(open("database.pickle", 'rb'))
		print (database)
	except:
		database = {}
	# threading.Thread(target=sendToPeople).start()
	main()

