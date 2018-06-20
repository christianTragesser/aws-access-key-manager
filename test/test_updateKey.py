import pytest
import datetime
import sys, os
import botocore.session
from botocore.stub import Stubber
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import updateKey

today = datetime.datetime.now()
expireDays = (datetime.datetime.now() - datetime.timedelta(days=90))
validDays = (datetime.datetime.now() - datetime.timedelta(days=20))

createResponse = {
  'AccessKey': {
    'UserName': 'test1',
    'AccessKeyId': '33333333333333333333',
    'Status': 'Active',
    'SecretAccessKey': 'ASDFGHJKLZXCVBNM',
    'CreateDate': today
  }
}

oneListResponse = {
  'AccessKeyMetadata': [
    {
      'UserName': 'test1',
      'AccessKeyId': '44444444444444444444',
      'Status': 'Inactive',
      'CreateDate': expireDays
    }
  ],
  'IsTruncated': False,
  'Marker': 'string'
}

twoListResponse = {
  'AccessKeyMetadata': [
    {
      'UserName': 'test1',
      'AccessKeyId': '11111111111111111111',
      'Status': 'Inactive',
      'CreateDate': datetime.datetime(2015, 1, 1)
    },
    {
      'UserName': 'test1',
      'AccessKeyId': '22222222222222222222',
      'Status': 'Inactive',
      'CreateDate': expireDays
    }
  ],
  'IsTruncated': False,
  'Marker': 'string'
}

activeListResponse = {
  'AccessKeyMetadata': [
    {
      'UserName': 'test1',
      'AccessKeyId': '11111111111111111111',
      'Status': 'Active',
      'CreateDate': validDays
    },
    {
      'UserName': 'test1',
      'AccessKeyId': '22222222222222222222',
      'Status': 'Inactive',
      'CreateDate': expireDays
    }
  ],
  'IsTruncated': False,
  'Marker': 'string'
}

deleteResponse = {
  'ResponseMetadata': {
    'RetryAttempts': 0,
    'HTTPStatusCode': 200,
    'RequestId': '5c150b58-7044-11e8-989d-b1e92028a197',
    'HTTPHeaders': {
      'x-amzn-requestid': '5c150b58-7044-11e8-989d-b1e92028a197',
      'date': 'Fri, 15 Jun 2018 02:32:33 GMT',
      'content-length': '210',
      'content-type': 'text/xml'
     }
  }
}

stubber = Stubber(updateKey.client)


def test_evaluate_one_inactive_user():
  # takes in user with single inactive key
  # create new key
  # return new key Id and secret key
  # returns 0 for deleted key
  stubber.add_response('list_access_keys', oneListResponse, {'UserName': 'test1'})
  stubber.add_response('create_access_key', createResponse, {'UserName': 'test1'})
  stubber.activate()

  response = updateKey.evalUserKeys('test1')

  stubber.assert_no_pending_responses()
  stubber.deactivate()
  assert response['user'] == 'test1'
  assert response['newKey']['AccessKeyId'] == '33333333333333333333'
  assert response['newKey']['SecretAccessKey'] == 'ASDFGHJKLZXCVBNM'
  assert response['deleteKey'] == 0

def test_evaluate_two_inactive_user():
  # takes in user with two inactive keys
  # evaluates number of Inactive keys
  # if more than one Inactive keys, delete oldest key
  # create new key
  # return new key Id and secret key
  stubber.add_response('list_access_keys', twoListResponse, {'UserName': 'test1'})
  stubber.add_response('delete_access_key', deleteResponse, {'UserName': 'test1', 'AccessKeyId': '11111111111111111111'})
  stubber.add_response('create_access_key', createResponse, {'UserName': 'test1'})
  stubber.activate()

  response = updateKey.evalUserKeys('test1')

  stubber.assert_no_pending_responses()
  stubber.deactivate()
  assert response['user'] == 'test1'
  assert response['newKey']['AccessKeyId'] == '33333333333333333333'
  assert response['newKey']['SecretAccessKey'] == 'ASDFGHJKLZXCVBNM'
  assert response['deleteKey'] == '11111111111111111111'

def test_evaluate_one_active_one_inactive_user():
  # takes in user with one valid active key and one inactive key
  # determines upgrade user had two active keys
  # returns no deleted key, returns no new key
  stubber.add_response('list_access_keys', activeListResponse, {'UserName': 'test1'})
  stubber.activate()

  response = updateKey.evalUserKeys('test1')

  stubber.assert_no_pending_responses()
  stubber.deactivate()
  assert response['user'] == 'test1'
  assert response['newKey'] == 0
  assert response['deleteKey'] == 0