import boto3
import json
import paho.mqtt.client as mqtt
import hmac
import hashlib
import base64


# Cognito info
cognito_app_client_id = "cognito_app_client_id"
cognito_user_pool_id = "cognito_user_pool_id"
cognito_region = "us-east-1"
cognito_identity_pool_id = "cognito_identity_pool_id"
client_secret = "client_secret"
username = "test2"
password = "Test1234."

# IoT Core info
iot_endpoint = "xxxxxxxxxxxx-ats.iot.us-east-1.amazonaws.com"
iot_port = 8883
iot_topic = "device/1"


def calculate_secret_hash(username, cognito_app_client_id, client_secret):
    message = username + cognito_app_client_id
    digest = hmac.new(str(client_secret).encode('utf-8'), msg=message.encode('utf-8'), digestmod=hashlib.sha256).digest()
    secret_hash = base64.b64encode(digest).decode()
    return secret_hash

secret_hash = calculate_secret_hash(username, cognito_app_client_id, client_secret)


# Authentication with Cognito
cognito = boto3.client("cognito-idp")
response = cognito.admin_set_user_password(
    UserPoolId=cognito_user_pool_id,
    Username=username,
    Password=password,
    Permanent=True
)

response = cognito.initiate_auth(
    AuthFlow="USER_PASSWORD_AUTH",
    AuthParameters={
        "USERNAME": username,
        "PASSWORD": password, 
        "SECRET_HASH": secret_hash
    },
    ClientId=cognito_app_client_id
    
)

cognito_id_token = response["AuthenticationResult"]["IdToken"]
print(response)


# Mqtt Client configuration
mqtt_client = mqtt.Client(protocol=mqtt.MQTTv5)
mqtt_client.username_pw_set(username=username, password=cognito_id_token)
mqtt_client.connect(iot_endpoint, iot_port, keepalive=60)

t = 20
h = 50

for i in range(10):
    
    data = {
        "temperature": t+i,
        "humidity": h+i
    }
    print(data)
    mqtt_client.publish(iot_topic, json.dumps(data),1)

mqtt_client.disconnect()