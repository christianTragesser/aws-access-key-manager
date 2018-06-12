import requests
import json

def webHook_message(slackurl, title, text, color):
    message_header = {'Content-type': 'application/json'}
    message = {}
    message['fallback'] = title
    message['color'] = color 
    message['fields'] = [
        {
            'title': title,
            'value': text,
            'short': False,
	    'mrkdwn': True
        }
    ]   
    payload = {}
    payload['attachments'] = [message]
    
    requests.post(slackurl, data=json.dumps(payload), headers=message_header)
