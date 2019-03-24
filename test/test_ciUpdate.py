import pytest
import datetime
import os
import mock
import responses
import ciUpdate


updateEvents = [
  {
    'warn': [],
    'expired': ['22222222222222222222'],
    'update': {
      'newKey': {
        'UserName': 'ci.user',
        'Status': 'Active',
        'CreateDate': datetime.datetime(2018, 6, 17, 1, 48, 47, 496389),
        'SecretAccessKey': 'ASDFGHJKLZXCVBNM',
        'AccessKeyId': '33333333333333333333'
      },
      'user': 'ci.user',
      'deleteKey': '11111111111111111111'
    },
    'user': 'ci.user'
  }
]

os.environ['CI_API_URL'] = 'http://ci-server.com'
os.environ['CI_API_TOKEN'] = 'ASDFGHJKL12345' 

def test_evaluate_ci_payload():
  # Takes in list of update events
  # constructs CI variable key/values
  payload = ciUpdate.createPayload(updateEvents)

  assert payload['url'] == 'http://ci-server.com'
  assert payload['token'] == 'ASDFGHJKL12345'
  assert payload['updates'][0]['user'] == 'CI.USER'
  assert payload['updates'][0]['idKey'] == '33333333333333333333'
  assert payload['updates'][0]['secretKey'] == 'ASDFGHJKLZXCVBNM'

samplePayload = {
  'url': 'http://ci-server.com',
  'token': 'ASDFGHJKL12345', 
  'updates': [{'secretKey': 'ASDFGHJKLZXCVBNM', 'idKey': '33333333333333333333', 'user': 'CI.USER'}]
}

@responses.activate
@mock.patch('ciUpdate.updateVar')
def test_evaluate_ci_update(mock_update_var):
  # checks CI API for variable key
  # if CI variable key found, update via CI API
  responses.add(responses.GET, 'http://ci-server.com/CI.USER_AWS_ACCESS_KEY_ID', status=200)
  ciUpdate.updateVariables(samplePayload)

  assert mock_update_var.called

@responses.activate
@mock.patch('ciUpdate.createVar')
def test_evaluate_ci_create(mock_create_var):
  # checks CI API for variable key
  # if CI variable key not found, create variable via CI API
  responses.add(responses.GET, 'http://ci-server.com/CI.USER_AWS_ACCESS_KEY_ID', status=404)
  ciUpdate.updateVariables(samplePayload)

  assert mock_create_var.called