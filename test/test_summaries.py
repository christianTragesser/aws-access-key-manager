import os, sys, json
import mock
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import summaries

expireResponse = [
  {'warn': [{'key': '11111111111111111111', 'ttl': 5}], 'expired': [], 'user': 'test1'},
  {'warn': [], 'expired': ['22222222222222222222'], 'user': 'test2'},
  {'warn': [{'key': '44444444444444444444', 'ttl': 3}], 'expired': ['55555555555555555555'], 'user': 'test3'}
]

# Construct warning and expire summaries
# log summaries
# return summarie
def test_construct_summary_func():
  # Takes in list of dicts describing warn/expire events
  # Constructs expire actions summary of user and key Id
  # Constructs warning summary of user, key id, and time-to-live
  messages = summaries.keyMessages(expireResponse)
  assert messages['warnings'][0] == 'User: *test1*, Key Id: 11111111111111111111     *5* days remaining\n'
  assert messages['warnings'][1] == 'User: *test3*, Key Id: 44444444444444444444     *3* days remaining\n'
  assert messages['expirations'][0] == 'User: *test2*, Key Id: 22222222222222222222 *now inactive*\n'
  assert messages['expirations'][1] == 'User: *test3*, Key Id: 55555555555555555555 *now inactive*\n'

@mock.patch('slack.webHook_message')
# Takes in list of warning and expire events
# Sends warning and expire messages to Slack webhook and system logs
def test_get_summary_func(mock_slack_message):
  messages = summaries.keyMessages(expireResponse)
  summary = summaries.summary(messages, 90, 'https://slackurl.com')
  
  assert mock_slack_message.called
  assert summary['expire'] == ('The following keys are older than 90 days and *have expired*:\n'
                             'User: *test2*, Key Id: 22222222222222222222 *now inactive*\n'
                             'User: *test3*, Key Id: 55555555555555555555 *now inactive*\n')
  assert summary['warn'] == ('The following keys are close to expiration(90 days).  Please renew soon:\n'
                                'User: *test1*, Key Id: 11111111111111111111     *5* days remaining\n'
                                'User: *test3*, Key Id: 44444444444444444444     *3* days remaining\n')