import boto3

client = boto3.client('iam')

def createUserKey(user):
    return client.create_access_key(UserName=user)