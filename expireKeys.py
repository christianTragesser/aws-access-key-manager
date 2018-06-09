import boto3
import datetime

client = boto3.client('iam')

def examineKeyAge(keys, warnDays, expireDays):
  warn = (datetime.datetime.now() - datetime.timedelta(days=warnDays)).date()
  expire = (datetime.datetime.now() - datetime.timedelta(days=expireDays)).date()

  issueKeys = {}
  warnKeys = []
  expireKeys = []

  for data in keys['AccessKeyMetadata']:
    if data['Status'] == 'Active':
      createDate = data['CreateDate'].date()
      if createDate <= expire:
        client.update_access_key(AccessKeyId=data['AccessKeyId'],
          UserName=data['UserName'],
          Status='Inactive'
        )
        expireKeys.append(data['AccessKeyId'])
      elif createDate <= warn:
        ttl = (createDate - expire).days
        warnInstance = {}
        warnInstance['key'] = data['AccessKeyId']
        warnInstance['ttl'] = ttl
        warnKeys.append(warnInstance)
      else:
        continue

  issueKeys = { "warn": warnKeys, "expired": expireKeys }

  return issueKeys


def getIssueUsers(warn, expire):
  issueUsers = []

  users = client.list_users()

  for user in users['Users']:
    keys = client.list_access_keys(UserName=user['UserName'])
    issueKeys = examineKeyAge(keys, warn, expire)
    issueUsers.append({ 'user': user['UserName'], 'warn': issueKeys['warn'], 'expired': issueKeys['expired'] })

  print issueUsers
  return issueUsers

if __name__ == "__main__":
  users = getIssueUsers(85, 90)
  print users