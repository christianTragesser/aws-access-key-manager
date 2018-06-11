def keyMessages(events):
    messages = {}
    messages['warnings'] = []
    messages['expirations'] = []
    for event in events:
        for key in event['warn']:
            warnEvent = 'User: %s, Key Id: %s - %d days remaining\n' % ( event['user'], key['key'], key['ttl'])
            messages['warnings'].append(warnEvent)

        for key in event['expired']:
            expireEvent = 'User: %s, Key Id: %s - now inactive\n' % ( event['user'], key)
            messages['expirations'].append(expireEvent)

    return messages

def summary(messages, expireDays):
  summary = {}
  if len(messages['expirations']) > 0:
    notice = "The following keys are older than %d and have expired:\n" % expireDays
    for message in messages['expirations']:
      notice += message
    summary['warn'] = notice

  if len(messages['warnings']) > 0:
    notice = "The following keys are close to expiration(%d days).  Please renew soon:\n" % expireDays
    for message in messages['warnings']:
      notice += message
    summary['expire'] = notice
  
  return summary