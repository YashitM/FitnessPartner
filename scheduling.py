TOKEN = "439442918:AAFtoa3vmZ9uvBc3eNYojEVXXGm2GkTYmAE"
from telegram.ext import Updater, CommandHandler
import logging
import time
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)

logger = logging.getLogger(__name__)
reminders = {}
def start(bot, update):
	update.message.reply_text('Hi! Use /set <24 hr time><space><reason> to set a reminder')



def alarm(bot, job):
	bot.send_message(job.context, text = reminders[job.context]['reason'])


def set_timer(bot, update, args, job_queue, chat_data):
	prevupdate = update
	print (len(args))
	chat_id = prevupdate.message.chat_id
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
		
		reminders[chat_id] = {'time': args[0], 'reason': reason}
		job = job_queue.run_repeating(alarm, context = chat_id, interval = 86400, first = total)
		chat_data[chat_id] = job

		update.message.reply_text('Reminder successfully set!')

	except (IndexError, ValueError):
		update.message.reply_text('Usage: /set <24 hr time><space><reason>')


def unset(bot, update, args, chat_data):
	if update.message.chat.id not in chat_data:
		update.message.reply_text('You have no active timer')
		return

	job = chat_data[update.message.chat.id]
	job.schedule_removal()
	del chat_data[update.message.chat.id]
	update.message.reply_text('Timer successfully unset!')


def error(bot, update, error):
	logger.warning('Update "%s" caused error "%s"', update, error)


def main():
	updater = Updater(TOKEN)
	dp = updater.dispatcher
	dp.add_handler(CommandHandler("start", start))
	dp.add_handler(CommandHandler("help", start))
	dp.add_handler(CommandHandler("set", set_timer,
								  pass_args = True,
								  pass_job_queue = True,
								  pass_chat_data = True))
	dp.add_handler(CommandHandler("unset", unset, pass_chat_data=True, pass_args=True))
	dp.add_error_handler(error)
	updater.start_polling()
	updater.idle()


if __name__ == '__main__':
	main()