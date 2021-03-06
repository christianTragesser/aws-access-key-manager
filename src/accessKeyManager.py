import os, sys
from pythonjsonlogger import jsonlogger
import logging
import expireKeys
import summaries
import updateKey

# set up logging
logging.basicConfig(stream=sys.stdout, level=logging.WARN)
log = logging.getLogger(__name__)
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
log.addHandler(logHandler)

# check of optional env var
warning = int(os.environ['WARN_DAYS']) if "WARN_DAYS" in os.environ else 85
expiration = int(os.environ['EXPIRE_DAYS']) if "EXPIRE_DAYS" in os.environ else 90
userWhiteList = os.environ['UPDATE_USERS'] if "UPDATE_USERS" in os.environ else ''
updateKeyUserList = [x.strip() for x in userWhiteList.split(',')]

def handler(event, context):
  # must supply Slack webhook to report automated events
  if "SLACK_URL" not in os.environ:
    log.error('SLACK_URL environment variable not set, we out!')
    sys.exit(1)
  else:
    slack_url = os.environ['SLACK_URL']
  
  try:  
    # gather list of users with warn or expired keys
    issueUsers = expireKeys.getIssueUsers(warning, expiration)
  except Exception as e:
    log.error(e.message)
    sys.exit(1)

  if len(issueUsers) > 0:
    if len(updateKeyUserList) == 0:
      log.info('No auto-update users listed, skipping auto-update of service account keys.')
    else:
      # if update-users exists, check warn/expired events for auto-update
      try:
        for event in issueUsers:
          if event['user'] in updateKeyUserList:
            event['update'] = updateKey.evalUserKeys(event['user'])
      except Exception as e:
        log.error(e.message)
        sys.exit(1)

    try:
      # Construct event messages and send via Slack webhook
      eventMessages = summaries.keyMessages(issueUsers)
      summary = summaries.summary(eventMessages, expiration, slack_url)
      log.warn(summary)
    except Exception as e:
      log.error(e.message)
      sys.exit(1)

if __name__ == '__main__':
  handler(1, 2)