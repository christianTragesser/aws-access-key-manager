import pytest
import datetime
import sys, os
import botocore.session
from botocore.stub import Stubber
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import expireKeys

# Warn after 85 days, expire after 90
warning = 85
expiration = 90
sample = 87 # should be greater than warning, less than expiration

# testing against logic involving time, set dates which can be asserted
def setDates(warn, expire):
    today = datetime.datetime.now()
    sampleDays = (datetime.datetime.now() - datetime.timedelta(days=sample))
    warnDays = (datetime.datetime.now() - datetime.timedelta(days=warn))
    expireDays = (datetime.datetime.now() - datetime.timedelta(days=expire))

    dates = {}
    dates['today'] = today
    dates['sampleDate'] = sampleDays
    dates['warnDate'] = warnDays
    dates['expireDate'] = expireDays
    return dates

date = setDates(warning, expiration)
usersResponse = {
  "Users": [
    {
      "Arn": "arn:aws:iam::123456789012:user/test1",
      "CreateDate": datetime.datetime(2018, 4, 28, 16, 38, 14),
      "PasswordLastUsed": date['today'],
      "Path": "/",
      "UserId": "AID2MAB8DPLSRHEXAMPLE",
      "UserName": "test1"
    },
    {
      "Arn": "arn:aws:iam::123456789012:user/test2",
      "CreateDate": datetime.datetime(2018, 4, 28, 16, 38, 14),
      "PasswordLastUsed": date['today'],
      "Path": "/",
      "UserId": "AIDIODR4TAW7CSEXAMPLE",
      "UserName": "test2"
    },
    {
      "Arn": "arn:aws:iam::123456789012:user/test3",
      "CreateDate": datetime.datetime(2018, 4, 28, 16, 38, 14),
      "PasswordLastUsed": date['today'],
      "Path": "/",
      "UserId": "AIDTKWGCODQAEXAMPLE",
      "UserName": "test3"
    }
  ]
} 

test1KeysResponse = {
  "AccessKeyMetadata": [
    {
      "UserName": "test1",
      "AccessKeyId": "11111111111111111111",
      "Status": "Active",
      "CreateDate": date['warnDate']
    },
  ],
  "IsTruncated": False,
  "Marker": "string"
}

test2KeysResponse = {
  "AccessKeyMetadata": [
    {
      "UserName": "test2",
      "AccessKeyId": "22222222222222222222",
      "Status": "Active",
      "CreateDate": date['expireDate']
    },
    {
      "UserName": "test2",
      "AccessKeyId": "33333333333333333333",
      "Status": "Inactive",
      "CreateDate": date['warnDate']
    },
  ],
  "IsTruncated": False,
  "Marker": "string"
}

test3KeysResponse = {
  "AccessKeyMetadata": [
    {
      "UserName": "test3",
      "AccessKeyId": "44444444444444444444",
      "Status": "Active",
      "CreateDate": date['sampleDate']
    },
    {
      "UserName": "test3",
      "AccessKeyId": "55555555555555555555",
      "Status": "Active",
      "CreateDate": date['expireDate']
    },
  ],
  "IsTruncated": False,
  "Marker": "string"
}

updateResponse = {
  'ResponseMetadata': {
    'RetryAttempts': 0,
    'HTTPStatusCode': 200,
    'RequestId': '3e015bc2-6ac8-11e8-b630-1fa11ee69c5c',
    'HTTPHeaders': {
      'x-amzn-requestid': '3e015bc2-6ac8-11e8-b630-1fa11ee69c5c',
      'date': date['today'],
      'content-length': '210',
      'content-type': 'text/xml'
    }
  }
}

stubber = Stubber(expireKeys.client)

def test_issue_users_dict():
  # takes list of IAM users
  # gets all keys for each user
  # determines warn and expired keys
  # set expired keys to Inactive
  # return dict with list of warning keys + days remaining and a list of keys set to Inactive
  stubber.add_response('list_users', usersResponse, {})
  stubber.add_response('list_access_keys', test1KeysResponse, {'UserName': 'test1'})
  stubber.add_response('list_access_keys', test2KeysResponse, {'UserName': 'test2'})
  stubber.add_response('update_access_key', updateResponse, {'AccessKeyId': '22222222222222222222', 'UserName': 'test2', 'Status': 'Inactive'})
  stubber.add_response('list_access_keys', test3KeysResponse, {'UserName': 'test3'})
  stubber.add_response('update_access_key', updateResponse, {'AccessKeyId': '55555555555555555555', 'UserName': 'test3', 'Status': 'Inactive'})
  stubber.activate()

  users = expireKeys.getIssueUsers(warning, expiration)

  stubber.assert_no_pending_responses()
  stubber.deactivate()
  # User test1:
  # - should have a key which warns and ttl
  # - should not have any expired keys
  assert users[0]['user'] == usersResponse['Users'][0]['UserName']
  assert users[0]['warn'][0]['ttl'] == (date['warnDate'].date() - date['expireDate'].date()).days
  assert users[0]['warn'][0]['key'] == test1KeysResponse['AccessKeyMetadata'][0]['AccessKeyId']
  assert len(users[0]['expired']) == 0

  # User test2:
  # - should have an expired key
  # - should not have any warn keys
  assert users[1]['user'] == usersResponse['Users'][1]['UserName']
  assert len(users[1]['warn']) == 0
  assert users[1]['expired'][0] == test2KeysResponse['AccessKeyMetadata'][0]['AccessKeyId']

  # User test3:
  # - should have a key which warns; ttl of expire - sample difference
  # - should have a expired key
  assert users[2]['user'] == usersResponse['Users'][2]['UserName']
  assert users[2]['warn'][0]['ttl'] == (date['sampleDate'].date() - date['expireDate'].date()).days
  assert users[2]['warn'][0]['key'] == test3KeysResponse['AccessKeyMetadata'][0]['AccessKeyId']
  assert users[2]['expired'][0] == test3KeysResponse['AccessKeyMetadata'][1]['AccessKeyId']
