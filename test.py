one = "0056"
import time

total = 0
if int(time.ctime()[11:13]) <= int(args[0][0:2]) and int(time.ctime()[11:13]) <= int(args[0][0:2]):
	total += 3600 * (int(args[0][0:2]) - int(time.ctime()[11:13]))
	total += 60 * (int(args[0][2:]) - int(time.ctime()[14:16]))
elif int(time.ctime()[11:13]) <= int(args[0][0:2]) and int(time.ctime()[11:13]) > int(args[0][0:2]):
	total += 3600 * (int(args[0][0:2]) - int(time.ctime()[11:13]))
	total -= 60 * (int(time.ctime()[14:16]) - int(args[0][2:]))
elif int(time.ctime()[11:13]) > int(args[0][0:2]) and int(time.ctime()[11:13]) < int(args[0][0:2]):
	total += 3600 * ((24 - int(time.ctime()[11:13])) + (int(args[0][0:2])))
	total += 60 * (int(args[0][2:]) - int(time.ctime()[14:16]))
else:
	total += 3600 * ((24 - int(time.ctime()[11:13])) + (int(args[0][0:2])))
	total -= 60 * (int(time.ctime()[14:16]) - int(args[0][2:]))

print (total)