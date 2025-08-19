from finalsa.common.models import to_sqs_message_attributes
from finalsa.sns.client.interface.client import SnsClient
from typing import Union, Dict, List, Optional
from pydantic import BaseModel
import logging
import boto3


class SnsClientImpl(SnsClient):

    def __init__(
        self
    ) -> None:
        self.resource = None
        self.client = None
        self.logger = logging.getLogger("finalsa.clients")
        self.cache = {}

    def get_resource(self):
        if self.resource is None:
            self.resource = boto3.resource('sns')
        return self.resource

    def get_client(self):
        if self.client is None:
            self.client = boto3.client('sns')
        return self.client

    def create_topic(self, name: str):
        try:
            topic = self.get_resource().create_topic(Name=name)
            self.logger.info("Created topic %s with ARN %s.", name, topic.arn)
        except Exception as ex:
            self.logger.error("Couldn't create topic %s.", name)
            self.logger.exception(ex)
            raise ex
        return topic

    def subscription_exists(
        self,
        topic_name: str,
        arn: str
    ) -> bool:
        try:
            subscriptions = self.list_subscriptions(topic_name)
            for sub in subscriptions:
                if sub['Endpoint'] == arn:
                    return True
        except Exception as e:
            self.logger.error("Subscription doesn't exist.")
            self.logger.exception(e)
        return False

    def get_all_topics(self) -> List:
        try:
            topics_iter = self.get_resource().topics.all()
            self.logger.debug("Got topics.")
            return topics_iter
        except Exception as ex:
            self.logger.error("Couldn't get topics.")
            self.logger.exception(ex)
            raise ex

    def get_or_create_topic(self, name: str):
        try:
            topic = self.get_topic(name)
        except Exception as e:
            self.logger.error(
                "Couldn't get topic %s. Creating it.", name)
            self.logger.exception(e)
            topic = self.create_topic(name)
        return topic

    def get_topic(self, topic_name: str):
        if topic_name in self.cache:
            return self.cache[topic_name]
        topic = None
        try:
            topics_iter = self.get_all_topics()
            topics_iter = filter(
                lambda t: t.arn.endswith(topic_name), topics_iter)
            topics = list(topics_iter)
            if len(topics) == 0:
                raise Exception("Topic not found.")
            self.logger.debug("Got topic.")
            topic = topics[0]
            self.cache[topic_name] = topic
        except Exception as e:
            self.logger.error("Couldn't get topics.")
            self.logger.exception(e)
            raise e
        else:
            return topic

    def list_subscriptions(self, topic: str) -> List:
        try:
            topic = self.get_topic(topic)
            return self.get_client().list_subscriptions_by_topic(
                TopicArn=topic.arn)['Subscriptions']
        except Exception as ex:
            self.logger.error("Couldn't get subscriptions.")
            self.logger.exception(ex)
            raise ex

    def subscribe(self, topic_name: str, protocol: str, endpoint: str) -> Dict:
        topic = self.get_topic(topic_name)
        try:
            subscription = self.get_client().subscribe(
                TopicArn=topic.arn,
                Protocol=protocol, Endpoint=endpoint)
            self.logger.info(
                "Subscribed %s to topic %s with protocol %s.",
                endpoint, topic.arn, protocol)
        except Exception as e:
            self.logger.error(
                "Couldn't subscribe %s to topic %s with protocol %s.",
                endpoint, topic.arn, protocol)
            self.logger.exception(e)
            raise e
        else:
            return subscription

    def publish_batch(self, topic_name: str, payloads: List[Union[Dict, BaseModel]], attrs: Dict | None = ...) -> List[Dict]:
        topic = self.get_topic(topic_name)
        attrs = attrs or {}
        entries = self.__dump_batch_payload__(payloads, to_sqs_message_attributes(attrs))
        groups = []
        counter = 0
        helper = []
        for entry in entries:
            if counter == 10:
                groups.append(helper.copy())
                helper.clear()
                counter = 0
            helper.append(entry)
            counter += 1
        if len(helper) > 0:
            groups.append(helper.copy())
        responses = []
        for group in groups:
            try:
                response = self.get_client().publish_batch(
                    TopicArn=topic.arn,
                    PublishBatchRequestEntries=group
                )
                responses.append(response)
            except Exception as e:
                self.logger.error("Failed to publish batch for group: %s", group)
                self.logger.exception(e)
                responses.append({'Error': str(e), 'Group': group})
        return responses

    def publish(
        self,
        topic_name: str,
        payload: Union[Dict, str],
        attrs: Optional[Dict] = None
    ) -> Dict:
        """
        Publish a message to a topic.
        """
        attrs = attrs or {}
        topic = self.get_topic(topic_name)
        if isinstance(payload, dict):
            payload = SnsClientImpl.__dump_payload__(payload)
        response = topic.publish(
            Message=payload,
            MessageAttributes=to_sqs_message_attributes(attrs)
        )
        message_id = response['MessageId']
        self.logger.info(
            "Published message to topic %s.", topic.arn)
        return {
            'id': message_id,
            'topic': topic.arn,
            'payload': payload,
        }
