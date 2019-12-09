#! /usr/bin/env python3

'''
Initiate connectivity test of a CPE device (Raspberry Pi) and resolve the test outcome.

'''

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import argparse
import json
import threading

testSucceed = False
testConcluded = threading.Event()

myAWSIoTMQTTClient = None
iotEndpoint = "a1be8p39z8xzwv-ats.iot.ap-southeast-2.amazonaws.com"
iotRootCA = "/home/zhanggy/aws/iot-certs/Amazon-root-CA-1.pem"
clientCert = "/home/zhanggy/aws/iot-certs/device.pem.crt"
privateKey = "/home/zhanggy/aws/iot-certs/private.pem.key"
clientId = "cpeTestRequester"
topicRequest = "tch/au/cts/test/cpe/connect/request"
topicOutcome = "tch/au/cts/test/cpe/connect/outcome"
req = {
    "request": "ping",
    "target": "8.8.8.8",
    "token": "none",
    "timestamp": "none"
}

# Configure logging
if __name__ == "__main__":
    logger = logging.getLogger("cpeConnectivityTest")
else:
    logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)


# Callback to print the test outcome
def checkOutcome(client, userdata, message):
    '''
    Callback executed when message received for topic tch/au/cts/test/cpe/connect/outcome.
    Verify the test result carried in the message and set thread event.

    Args: AWS SDK standard parameters
    Returns: none
    '''
    data = message.payload
    logger.info("Received test outcome: %s", data.decode('utf-8'))

    try:
        if json.loads(message.payload)["result"] == "succeed":
            global testSucceed
            testSucceed = True
        testConcluded.set()
    except KeyError:
        print("Not an expected test outcome.\n")


def clientInit(customCallback, useWebsocket=False):
    '''
    Initialize AWS IoT client and subscribe to topic for test request.
    By default use certificate and RSA key authentication configured in global variables.
    '''
    global myAWSIoTMQTTClient

    # Init AWSIoTMQTTClient
    if useWebsocket:
        myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId, useWebsocket=True)
        myAWSIoTMQTTClient.configureEndpoint(iotEndpoint, portNumber=443)
        myAWSIoTMQTTClient.configureCredentials(iotRootCA)
    else:
        myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
        myAWSIoTMQTTClient.configureEndpoint(iotEndpoint, portNumber=8883)
        myAWSIoTMQTTClient.configureCredentials(iotRootCA, privateKey, clientCert)

    # AWSIoTMQTTClient connection configuration
    myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
    myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
    myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
    myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

    # Connect and subscribe to AWS IoT
    myAWSIoTMQTTClient.connect()
    myAWSIoTMQTTClient.subscribe(topicOutcome, 1, customCallback)
    time.sleep(2)

def requestTest(targetIP="8.8.8.8"):
    '''
    Request a cpe device to start a connectivity test.
    By default test against google DNS server address.
    '''
    req["target"] = targetIP
    messageJson = json.dumps(req)
    myAWSIoTMQTTClient.publish(topicRequest, messageJson, 1)
    logger.info('Published test request: %s' % messageJson)


if __name__ == "__main__":
    # Read in command-line parameters
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--cert", action="store", dest="certificatePath", default=clientCert, help="Certificate file")
    parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", default=privateKey, help="Private key file")
    parser.add_argument("-w", "--websocket", action="store_true", dest="useWebsocket",
                        help="Use MQTT over WebSocket")
    parser.add_argument("-id", "--clientId", action="store", dest="clientId", default=clientId, 
                        help="Targeted client id")
    parser.add_argument("-t", "--topic", action="store", dest="topic", default=topicRequest, help="Targeted topic")

    args = parser.parse_args()
    clientCert = args.certificatePath
    privateKey = args.privateKeyPath
    useWebsocket = args.useWebsocket
    clientId = args.clientId
    topicRequest = args.topic

    if not args.useWebsocket and (not args.certificatePath or not args.privateKeyPath):
        parser.error("Missing credentials for authentication.")
        exit(2)

    print("CPE connectivity test in loop.\n")

    clientInit(checkOutcome, useWebsocket)
    requestTest()
    while True:
        while not testConcluded.wait(timeout=10):
            requestTest()
        
        if testSucceed:
            print("CPE connectivity test succeeded.\n")
        else:
            print("CPE connectivity test failed.\n")

        testConcluded.clear()
        testSucceed = False
