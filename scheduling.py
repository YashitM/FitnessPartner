TOKEN = "439442918:AAFtoa3vmZ9uvBc3eNYojEVXXGm2GkTYmAE"
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
						  ConversationHandler)
from telegram import Bot
import logging
import time
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)

logger = logging.getLogger(__name__)
chat_data = {}

SELECTREMOVE, ALARM = range(2)

def start(bot, update):
	update.message.reply_text('Hi! Use /set <24 hr time><space><reason> to set a reminder')
	return ConversationHandler.END


def alarmgym(bot, job):
	bot.send_message(job.context, text = "It's time for your exercise!")

def alarmmedicine(bot, job):
	bot.send_message(job.context, text = "It's time to take your medicine")


def set_timer(bot, update, args, job_queue, chat_data):
	print ("entered function")
	chat_id = update.message.chat_id
	try:
		total = 0
		reason = ""
		one = args[0]
		two = one[0:2]
		three = one[2:4]
		for i in range(1, len(args)):
			reason += args[i] + " "
		
		if int(time.ctime()[11:13]) <= int(two) and int(time.ctime()[11:13]) <= int(two):
			total += 3600 * (int(two) - int(time.ctime()[11:13]))
			total += 60 * (int(three) - int(time.ctime()[14:16]))
		elif int(time.ctime()[11:13]) <= int(two) and int(time.ctime()[11:13]) > int(two):
			total += 3600 * (int(two) - int(time.ctime()[11:13]))
			total -= 60 * (int(time.ctime()[14:16]) - int(three))
		elif int(time.ctime()[11:13]) > int(two) and int(time.ctime()[11:13]) < int(two):
			total += 3600 * ((24 - int(time.ctime()[11:13])) + (int(two)))
			total += 60 * (int(three) - int(time.ctime()[14:16]))
		else:
			total += 3600 * ((24 - int(time.ctime()[11:13])) + (int(two)))
			total -= 60 * (int(time.ctime()[14:16]) - int(three))
		if total < 0:
			update.message.reply_text('Sorry we can not go back to future!')
			return
		if "exercise" in reason:
			job = job_queue.run_repeating(alarmgym, context = chat_id, interval = 86400, first = total)
		else:
			job = job_queue.run_repeating(alarmmedicine, context = chat_id, interval = 86400, first = total)
		if chat_id not in chat_data:
			chat_data[chat_id] = []
		chat_data[chat_id].append({'Job': job, 'Time':args[0], 'Reason':reason})
		
		update.message.reply_text('Reminder successfully set!')

	except (IndexError, ValueError):
		update.message.reply_text('Usage: /set <24 hr time><space><reason>')
	return ConversationHandler.END

def unset(bot, update, args, chat_data):
	tosend = ""
	if len(chat_data[update.message.chat.id]) == 0:
		update.message.reply_text('You have no remainders set')
		return
	else:
		update.message.reply_text("please enter the time of the reminder you wish to delete from among the following")
		for _ in range(len(chat_data[update.message.chat.id])):
			tosend += (str(chat_data[update.message.chat.id][_]['Time']) + " : " + str(chat_data[update.message.chat.id][_]['Reason'])) + "\n"
		update.message.reply_text(tosend)
	return SELECTREMOVE
	

def removeset(bot, update, chat_data):
	for _ in range(len(chat_data[update.message.chat.id])):
		if chat_data[update.message.chat.id][_]['Time'] == update.message.text:
			job = chat_data[update.message.chat.id][_]['Job']
			chat_data[update.message.chat.id].remove(chat_data[update.message.chat.id][_])
			job.schedule_removal()
			break
	update.message.reply_text('Reminder Removed!')

	return ConversationHandler.END

def error(bot, update, error):
	logger.warning('Update "%s" caused error "%s"', update, error)


def main():
	updater = Updater(TOKEN)
	dp = updater.dispatcher
	conv_handler = ConversationHandler(
		entry_points=[CommandHandler("start", start), CommandHandler("help", start), CommandHandler("set", set_timer,
								  pass_args = True,
								  pass_job_queue = True,
								  pass_chat_data = True), CommandHandler("unset", unset, pass_chat_data=True, pass_args=True)],
		states={
			SELECTREMOVE: [MessageHandler(Filters.text, removeset, pass_chat_data = True)],
		},
		fallbacks=[]
	)
	dp.add_handler(conv_handler)
	dp.add_error_handler(error)
	updater.start_polling()
	updater.idle()


if __name__ == '__main__':

	main()