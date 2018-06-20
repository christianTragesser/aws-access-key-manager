import boto3
import datetime

client = boto3.client('iam')

def deleteUserKey(user, inactiveKeys):
  difference = inactiveKeys[0]['CreateDate'].date() - inactiveKeys[1]['CreateDate'].date()
  if difference.days <= 0:
    client.delete_access_key(UserName=user, AccessKeyId=inactiveKeys[0]['AccessKeyId'])
    return inactiveKeys[0]['AccessKeyId'] 
  else:
    client.delete_access_key(UserName=user, AccessKeyId=inactiveKeys[1]['AccessKeyId'])
    return inactiveKeys[1]['AccessKeyId']
    

def evalUserKeys(user):
  userInfo = {}
  inactiveKeys = []

  userInfo['user'] = user
  keys = client.list_access_keys(UserName=user)
  
  for key in keys['AccessKeyMetadata']:
    if key['Status'] == 'Inactive':
      inactiveKeys.append(key)

  if len(inactiveKeys) == 1 and len(keys['AccessKeyMetadata']) == 1:
    userInfo['deleteKey'] = 0
    newKey = client.create_access_key(UserName=user)
    userInfo['newKey'] = newKey['AccessKey']
  elif len(inactiveKeys) == 2:
    userInfo['deleteKey'] = deleteUserKey(user, inactiveKeys)
    newKey = client.create_access_key(UserName=user)
    userInfo['newKey'] = newKey['AccessKey']
  else:
    userInfo['deleteKey'] = 0
    userInfo['newKey'] = 0
  
  return userInfo