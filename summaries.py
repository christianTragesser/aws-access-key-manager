import slack

def keyMessages(events):
  messages = {}
  messages['warnings'] = []
  messages['expirations'] = []
  messages['updates'] = []
  for event in events:
    for key in event['warn']:
      warnEvent = 'User: *%s*, Key Id: %s     *%d* days remaining\n' % ( event['user'], key['key'], key['ttl'])
      messages['warnings'].append(warnEvent)

    for key in event['expired']:
      expireEvent = 'User: *%s*, Key Id: %s *now inactive*\n' % ( event['user'], key)
      messages['expirations'].append(expireEvent)

    if 'update' in event:
      if event['update']['newKey'] == 0 and event['update']['deleteKey'] == 0:
        updateEvent = 'Unable to auto-update user *%s*, existing additional active key.\n' % event['user']

      if event['update']['newKey'] != 0:
        updateEvent = 'User: *%s*, Key Id: %s *auto-update*\n' % ( event['user'],
                                                                  event['update']['newKey']['AccessKeyId'] )

      if event['update']['deleteKey'] != 0:
        updateEvent = updateEvent+'User: *%s*, Key Id: %s *deleted*\n' % ( event['user'], event['update']['deleteKey'] )

      messages['updates'].append(updateEvent)
  return messages

def summary(messages, expireDays, slackUrl):
  summary = {}
  if len(messages['expirations']) > 0:
    notice = "The following keys are older than %d days and *have expired*:\n" % expireDays
    for message in messages['expirations']:
      notice += message
    summary['expire'] = notice
    title = 'AWS access key expiration'
    color = 'danger'
    slack.webHook_message(slackUrl, title, notice, color)

  if len(messages['warnings']) > 0:
    notice = "The following keys are close to expiration(%d days).  Please renew soon:\n" % expireDays
    for message in messages['warnings']:
      notice += message
    summary['warn'] = notice
    title = 'AWS access key warning'
    color = 'warning'
    slack.webHook_message(slackUrl, title, notice, color)
  
  if len(messages['updates']) > 0:
    notice = "Auto-renew events:\n"
    for message in messages['updates']:
      notice += message
    summary['update'] = notice
    title = 'AWS access key change'
    color = 'warning'
    slack.webHook_message(slackUrl, title, notice, color)

  if len(messages['warnings']) > 0 or len(messages['expirations']) > 0:
    return summary