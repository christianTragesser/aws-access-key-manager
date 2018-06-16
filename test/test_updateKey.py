import boto3
import datetime
import sys, os
import botocore.session
from botocore.stub import Stubber
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import updateKey

today = datetime.datetime.now()
expireDays = (datetime.datetime.now() - datetime.timedelta(days=90))

listResponse = {
  'AccessKeyMetadata': [
    {
      'UserName': 'test1',
      'AccessKeyId': '11111111111111111111',
      'Status': 'Inactive',
      'CreateDate': datetime.datetime(2015, 1, 1)
    },
    {
      'UserName': 'test1',
      'AccessKeyId': '2222222222222222222',
      'Status': 'Inactive',
      'CreateDate': expireDays
    }
  ],
  'IsTruncated': False,
  'Marker': 'string'
}

createResponse = {
  'AccessKey': {
    'UserName': 'test1',
    'AccessKeyId': '33333333333333333333',
    'Status': 'Active',
    'SecretAccessKey': 'ASDFGHJKLZXCVBNM',
    'CreateDate': today
  }
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

def test_create_user_key():
# takes in user who gets new key created
# capture new key ID and key secret
# prepares key ID, key secret, and CI server variable update
# update CI server variable via API
  stubber.add_response('create_access_key', createResponse, {'UserName': 'test1'})
  stubber.activate()

  response = updateKey.createUserKey('test1')

  stubber.assert_no_pending_responses()
  stubber.deactivate()
  assert response['AccessKey']['AccessKeyId'] == '33333333333333333333'
  assert response['AccessKey']['SecretAccessKey'] == 'ASDFGHJKLZXCVBNM'