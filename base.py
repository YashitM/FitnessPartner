import requests

botToken = "348036998:AAFT0S0MKz8OLiE1FA1k9sfjhuAKtR1htzE"

url = "https://api.telegram.org/"+botToken+"/"

def get_updates_json(request):  
	response = requests.get(request + 'getUpdates')
	return response.json()
	
def last_update(data):  
	results = data['result']
	total_updates = len(results) - 1
	return results[total_updates]

print (url)