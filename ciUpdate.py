import requests
import os

def createPayload(events):
  payload = {}
  payload['url'] = os.environ['CI_API_URL'] if "CI_API_URL" in os.environ else ''
  payload['token'] = os.environ['CI_API_TOKEN'] if "CI_API_TOKEN" in os.environ else ''
  payload['updates'] = []
  for event in events:
    update = {}
    update['user'] = event['user'].upper()
    update['idKey'] = event['update']['newKey']['AccessKeyId']
    update['secretKey'] = event['update']['newKey']['SecretAccessKey']
    payload['updates'].append(update)
  print payload
  return payload

def updateVariables(payload):
  for update in payload['updates']:
    accessKeyIdKey = update['user']+'_AWS_ACCESS_KEY_ID'
    accessKeyIdVal = update['idKey']
    accessSecretKey = update['user']+'_AWS_SECRET_ACCESS_KEY'
    accessSecretVal = update['secretKey']
    varURL = payload['url']+'/'+accessKeyIdKey

    if detailVar(varURL, payload['token'], accessKeyIdKey):
      updateVar(varURL, payload['token'], accessKeyIdVal)
    else:
      createVar(payload['url'], payload['token'], accessKeyIdKey, accessKeyIdVal)

    if detailVar(varURL, payload['token'], accessSecretKey):
      updateVar(varURL, payload['token'], accessSecretVal)
    else:
      createVar(payload['url'], payload['token'], accessSecretKey, accessSecretVal)

def detailVar(url, token, ciVarKey):
  header = {'PRIVATE-TOKEN': token}
  r = requests.get(url, headers=header)
  print r
  if r.status_code == 200:
    return True
  else:
    return False

def createVar(url, token, ciVarKey, ciVarVal):
  header = {'PRIVATE-TOKEN': token}
  r = requests.post(url, data = {'key':ciVarKey,'value':ciVarVal}, headers=header)
  print r
  if r.status_code == 200:
    return True
  else:
    return False

def updateVar(url, token, ciVarVal):
  header = {'PRIVATE-TOKEN': token}
  r = requests.put(url, data = {'value':ciVarVal}, headers=header)
  print r
  if r.status_code == 200:
    return True
  else:
    return False