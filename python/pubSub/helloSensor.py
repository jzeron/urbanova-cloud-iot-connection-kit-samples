'''
Copyright Urbanova 2019
Licensed under the Apache License, Version 2.0
'''

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import argparse
import json


# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")


# Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Urbanova Cloud IoT Endpoint")
parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
parser.add_argument("-c", "--cert", action="store", required=True, dest="certificatePath", help="Certificate file path")
parser.add_argument("-k", "--key", action="store", required=True, dest="privateKeyPath", help="Private key file path")
parser.add_argument("-d", "--device", action="store", required=True, dest="deviceId", help="Device Identifier")

args = parser.parse_args()
ucIoTCustomEndpoint = "a1siobcc26zf4j-ats.iot.us-west-2.amazonaws.com" # Urbanova Cloud IoT Custom Endpoint / MQTT Broker hosted at AWS
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
deviceId = args.deviceId


# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)


# Create an Urbanova Cloud IoT MQTT Client using TLSv1.2 Mutual Authentication
ucIoTDeviceClient = None  # initialize object
ucIoTDeviceClient = AWSIoTMQTTClient(deviceId) # The client class that connects to and accesses AWS IoT over MQTT v3.1/3.1.1.
ucIoTDeviceClient.configureEndpoint(host, 8883)
ucIoTDeviceClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)


# Configure Urbanova Cloud IoT Device Client Connection Settings (reference: https://s3.amazonaws.com/aws-iot-device-sdk-python-docs/sphinx/html/index.html)
ucIoTDeviceClient.configureAutoReconnectBackoffTime(1, 32, 20)
ucIoTDeviceClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
ucIoTDeviceClient.configureDrainingFrequency(2)  # Draining: 2 Hz
ucIoTDeviceClient.configureConnectDisconnectTimeout(10)  # 10 sec
ucIoTDeviceClient.configureMQTTOperationTimeout(5)  # 5 sec


# Connect to Urbanova Cloud IoT
ucIoTDeviceClient.connect()
time.sleep(2)


# Publish `Hello Sensor ${sensorID}`to Urbanova Cloud once per second
loopCount = 0
while True:
  message['message'] = 'Hello Sensor ' + deviceId # add message element
  message['sequence'] = loopCount # add message element
  messageJson = json.dumps(message) # convert to json
  ucIoTDeviceClient.publish(deviceId, messageJson, 1) # publish to urbanova cloud
  print('Published to %s: %s\n' % (deviceId, messageJson)) # print console
  loopCount += 1 # increment counter
  time.sleep(1) # delay one second