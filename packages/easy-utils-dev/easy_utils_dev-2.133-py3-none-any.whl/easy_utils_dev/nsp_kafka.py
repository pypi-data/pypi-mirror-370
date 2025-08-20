import json
import os
import sys
import threading
import time
from logging import DEBUG, FileHandler, Formatter, Logger, getLogger
import requests
import urllib3
from dotenv import load_dotenv
from kafka import KafkaConsumer
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

semaphore = threading.Semaphore()


class TokenManager:
    def __init__(self, sever_ip: str, username: str, password: str, logger: Logger, access_token: str = None, refresh_token: str = None):
        self.server_ip = sever_ip
        self.username = username
        self.password = password
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.logger = logger
        retry_strategy = urllib3.Retry(total=4,  status_forcelist=[
            429, 500, 502, 503, 504])
        adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
        self.session = requests.Session()
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def login(self):
        headers = {
            'content_type': 'application/json',
        }
        body = {
            "grant_type": "client_credentials"
        }
        token_payload = self.session.post(f'https://{self.server_ip}/rest-gateway/rest/api/v1/auth/token', auth=requests.auth.HTTPBasicAuth(
            username=self.username, password=self.password), headers=headers, verify=False, json=body)
        if not token_payload.ok:
            logger.error(token_payload.text, token_payload.status_code)
            raise Exception("Could not get access token")
        else:
            logger.info('Successfully logged in for the first time')
        token_payload = json.loads(token_payload.text)
        self.access_token = token_payload['access_token']
        self.refresh_token = token_payload['refresh_token']

    def token_refresh(self):
        headers = {
            'content_type': 'application/json',
        }
        body = {
            "grant_type": "refresh_token",
            "refresh_token": f"{self.refresh_token}"
        }
        token_payload = self.session.post(f'https://{self.server_ip}/rest-gateway/rest/api/v1/auth/token', auth=requests.auth.HTTPBasicAuth(
            username=self.username, password=self.password), headers=headers, verify=False, json=body)
        if not token_payload.ok:
            logger.error(token_payload.text, token_payload.status_code)
            raise Exception("Could not get access token")
        else:
            logger.info("Successfully refreshed the token")
        token_payload = json.loads(token_payload.text)
        self.access_token = token_payload['access_token']
        self.refresh_token = token_payload['refresh_token']

    def logout(self):
        headers = {
            'content_type': 'application/x-www-form-urlencoded '
        }
        data = {
            'token': f'{self.access_token}',
            'token_type_hint': 'token'
        }
        self.session.post(f'https://{self.server_ip}/rest-gateway/rest/api/v1/auth/revocation', verify=False,
                          headers=headers, data=data, auth=requests.auth.HTTPBasicAuth(username=self.username, password=self.password))

    def refresh_token_thread(self):
        while True:
            semaphore.acquire()
            logger.info('starting token refresh job....')
            self.token_refresh()
            semaphore.release()
            time.sleep(3000)


class KafkaTopicManager:
    def __init__(self, server_ip: str = None, topic_id: str = None, sub_id: str = None, token: TokenManager = None, logger: Logger = Logger(name='nan')):
        self.server_ip = server_ip
        self.topic_id = topic_id
        self.sub_id = sub_id
        self.token = token
        self.logger = logger
        retry_strategy = urllib3.Retry(total=4,  status_forcelist=[
            429, 500, 502, 503, 504])
        adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
        self.session = requests.Session()
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def create_topic(self):
        headers = {
            'Authorization': f'Bearer {self.token.access_token}',
            'Content-Type': 'application/json'
        }
        create_subscription_body = {
            "categories": [
                {
                    "name": "NSP-FAULT",
                    "propertyFilter": "alarmName = 'ThresholdCrossingAlert' and affectedObjectType = 'sas.TWLSession'",
                    "advancedFilter": "{\"includeAlarmDetailsOnDeleteEvent\" :true}"
                }
            ]
        }
        create_subscription = self.session.post(
            f"https://{self.server_ip}/nbi-notification/api/v1/notifications/subscriptions", headers=headers, verify=False, json=create_subscription_body)
        if not create_subscription.ok:
            logger.error(
                f"Failed to create subscription. Error code is {create_subscription.status_code}. Text response is {create_subscription.text}")
            sys.exit(1)
        else:
            create_subscription = create_subscription.json()[
                'response']['data']
            self.sub_id = create_subscription['subscriptionId']
            self.topic_id = create_subscription['topicId']
            logger.info(f"Created subscription {self.sub_id}")

    def refresh_topic(self):
        headers = {
            'Authorization': f'Bearer {self.token.access_token}',
            'Content-Type': 'application/json'
        }
        renew_subscription = self.session.post(
            f"https://{self.server_ip}/nbi-notification/api/v1/notifications/subscriptions/{self.sub_id}/renewals", verify=False, headers=headers)
        if not renew_subscription.ok:
            logger.error(
                f'Failed to renew subscription. Error code is {renew_subscription.status_code} and response text is {renew_subscription.text}')
        else:
            logger.info(f"Renewed subscription {self.sub_id}")

    def refresh_topic_thread(self):
        while True:
            logger.info("starting topic refresh job....")
            semaphore.acquire()
            self.refresh_topic()
            semaphore.release()
            time.sleep(900)


if __name__ == "__main__":
    current_path = os.path.dirname(os.path.realpath(__file__))
    disable_warnings(InsecureRequestWarning)
    if not os.path.isdir(os.path.join(current_path, 'logs')):
        os.mkdir(os.path.join(current_path, 'logs'))
    my_handler = FileHandler(filename=os.path.join(
        current_path, 'logs', 'kafka_consumer.log'))
    my_handler.setFormatter(
        Formatter("[%(asctime)s]-%(levelname)s-%(module)s: %(message)s"))
    logger = getLogger('consumerLogger')
    logger.addHandler(my_handler)
    logger.setLevel(DEBUG)
    load_dotenv()
    nsp_ip = os.getenv('nsp_ip')
    nsp_username = os.getenv('nsp_username')
    nsp_password = os.getenv('nsp_password')
    wf_id = os.getenv('wf_id')

    token_manager = TokenManager(nsp_ip, nsp_username, nsp_password, logger)
    token_manager.login()
    topic_manager = KafkaTopicManager(
        server_ip=nsp_ip, token=token_manager, logger=logger)
    topic_manager.create_topic()
    token_refresh_job = threading.Thread(
        target=token_manager.refresh_token_thread)
    topic_refresh_job = threading.Thread(
        target=topic_manager.refresh_topic_thread)
    token_refresh_job.daemon = True
    topic_refresh_job.daemon = True
    token_refresh_job.start()
    topic_refresh_job.start()
    kafka_consumer = KafkaConsumer(
        topic_manager.topic_id,
        bootstrap_servers=f"{nsp_ip}:9192",
        security_protocol="SSL",
        ssl_cafile=os.path.join(current_path, "ca_cert.pem"),
        ssl_certfile=os.path.join(
            current_path, 'nsp.pem'),
        ssl_keyfile=os.path.join(current_path, 'nsp.key'),
        enable_auto_commit=True,
        auto_offset_reset='latest',
        key_deserializer=lambda m: m.decode('utf-8') if m else None,
        value_deserializer=lambda m: json.loads(
            m.decode('utf-8')) if m else None
    )

    try:
        while True:
            for message in kafka_consumer.poll(timeout_ms=1000).values():
                for record in message:
                    if ('data' in record.value.keys()) and ('nsp-fault:alarm-delete' in record.value['data']['ietf-restconf:notification'].keys() or 'nsp-fault:alarm-create' in record.value['data']['ietf-restconf:notification'].keys()):
                        logger.info(
                            f"Message received, message value is {record.value}")
                        trigger_wf_body = {
                            "workflow_id": f"{wf_id}",
                            "input": {
                                "input": record.value
                            },
                            "notifyKafka": True
                        }
                        trigger_wf = requests.post(
                            f"https://{nsp_ip}/wfm/api/v1/execution", json=trigger_wf_body, headers={'Authorization': f"Bearer {token_manager.access_token}"}, verify=False)
                        if not trigger_wf.ok:
                            logger.error(
                                f"Workflow failed to trigger. error code was {trigger_wf.status_code} and text was {trigger_wf.text}")
                        else:
                            logger.info("Workflow was triggered!")
                    else:
                        logger.info(
                            f"Message received, but was skipped as it is not create or delete. Skilled message was {record.value}")

    except KeyboardInterrupt:
        token_manager.logout()
        logger.info("Script stopped by user")
    except Exception as e:
        token_manager.logout()
        logger.error(f"Unforeseen error {e} happened")


#### This is how to get the pem /cert/nsp:

# kubectl  cp nsp-psa-restricted/nspos-kafka-0:/opt/nsp/os/ssl/certs/nsp/nsp.pem /tmp/nsp.pem
# kubectl  cp nsp-psa-restricted/nspos-kafka-0:/opt/nsp/os/ssl/ca_cert.pem /tmp/ca_cert.pem
# kubectl  cp nsp-psa-restricted/nspos-kafka-0:/opt/nsp/os/ssl/nsp.key /tmp/nsp.key

#### 7ot el nsp.key wel nsp.pem wel ca_cert.pem fe nafs el directoriy
 
##### we lama te run el script, use nohub 3ashan mayb2ash bound le terminal
## nohup python3.12 NSP_Kafka_Consumer_AE.py >> /scripts/UC3/logs/kafka_consumer.log 2>&1 &