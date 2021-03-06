import json
import mock
import datetime
import summaries

expireResponse = [
  {'warn': [{'key': '11111111111111111111', 'ttl': 5}], 'expired': [], 'user': 'test1'},
  {'warn': [], 'expired': ['22222222222222222222'], 'user': 'test2'},
  {'warn': [{'key': '44444444444444444444', 'ttl': 3}], 'expired': ['55555555555555555555'], 'user': 'test3'},
  {
    'warn': [],
    'expired': ['77777777777777777777'],
    'update': {
      'newKey': {
        'UserName': 'test4',
        'Status': 'Active',
        'CreateDate': datetime.datetime(2018, 6, 17, 1, 48, 47, 496389),
        'SecretAccessKey': 'ASDFGHJKLZXCVBNM',
        'AccessKeyId': '88888888888888888888'
      },
      'user': 'test4',
      'deleteKey': '66666666666666666666'
    },
    'user': 'test4'
  }
]

def test_construct_summary_func():
  # Takes in list of dicts describing warn/expire events
  # Constructs expire actions summary of user and key Id
  # Constructs warning summary of user, key id, and time-to-live
  messages = summaries.keyMessages(expireResponse)
  assert messages['warnings'][0] == 'User: *test1*, Key Id: 11111111111111111111     *5* days remaining\n'
  assert messages['warnings'][1] == 'User: *test3*, Key Id: 44444444444444444444     *3* days remaining\n'
  assert messages['expirations'][0] == 'User: *test2*, Key Id: 22222222222222222222 *now inactive*\n'
  assert messages['expirations'][1] == 'User: *test3*, Key Id: 55555555555555555555 *now inactive*\n'
  assert messages['updates'][0] == ('User: *test4*, Key Id: 88888888888888888888 *auto-update*\n'
                                    'User: *test4*, Key Id: 66666666666666666666 *deleted*\n')

@mock.patch('slack.webHook_message')
def test_get_summary_func(mock_slack_message):
  # Takes in list of warning and expire events
  # Sends warning and expire messages to Slack webhook and system logs
  messages = summaries.keyMessages(expireResponse)
  summary = summaries.summary(messages, 90, 'https://slackurl.com')
  
  assert mock_slack_message.called
  assert summary['expire'] == ('The following keys are older than 90 days and *have expired*:\n'
                             'User: *test2*, Key Id: 22222222222222222222 *now inactive*\n'
                             'User: *test3*, Key Id: 55555555555555555555 *now inactive*\n'
                             'User: *test4*, Key Id: 77777777777777777777 *now inactive*\n')
  assert summary['warn'] == ('The following keys are close to expiration(90 days).  Please renew soon:\n'
                                'User: *test1*, Key Id: 11111111111111111111     *5* days remaining\n'
                                'User: *test3*, Key Id: 44444444444444444444     *3* days remaining\n')
  assert summary['update'] == ('Auto-renew events:\n'
                                'User: *test4*, Key Id: 88888888888888888888 *auto-update*\n'
                                'User: *test4*, Key Id: 66666666666666666666 *deleted*\n')