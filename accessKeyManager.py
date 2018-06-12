import os, sys
from pythonjsonlogger import jsonlogger
import logging
import expireKeys
import summaries

logging.basicConfig(stream=sys.stdout, level=logging.WARN)
log = logging.getLogger(__name__)
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
log.addHandler(logHandler)

warning = int(os.environ['WARN_DAYS']) if "WARN_DAYS" in os.environ else 85
expiration = int(os.environ['EXPIRE_DAYS']) if "EXPIRE_DAYS" in os.environ else 90

def handler(event, context):
  if "SLACK_URL" not in os.environ:
    log.error('SLACK_URL environment variable not set, we out!')
    sys.exit(1)
  else:
    slack_url = os.environ['SLACK_URL']
    
  issueUsers = expireKeys.getIssueUsers(warning, expiration)
  if len(issueUsers) > 0:
    eventMessages = summaries.keyMessages(issueUsers)
    summary = summaries.summary(eventMessages, expiration, slack_url)
    log.warn(summary)

if __name__ == '__main__':
  handler(1, 2)