from finalsa.sns.client.interface import SnsClient
from pydantic import BaseModel
from typing import Union, Dict, Optional, List


class SnsClientTest(SnsClient):

    def __init__(
        self,
    ) -> None:
        self.topics = {}

    def create_topic(self, name: str):
        self.topics[name] = {
            "arn": f"arn:aws:sns:us-east-1:123456789012:{name}",
            "name": name,
            "id": "123456789012",
            "subscriptions": [],
            "messages": []
        }
        return self.topics[name]

    def subscription_exists(self, topic_name: str, arn: str) -> bool:
        if topic_name in self.topics:
            topic = self.topics[topic_name]
            for sub in topic['subscriptions']:
                if sub['Endpoint'] == arn:
                    return True
        return False

    def get_all_topics(self):
        return list(self.topics.keys())

    def get_or_create_topic(self, name: str):
        if name in self.topics:
            return self.topics[name]
        return self.create_topic(name)

    def get_topic(self, topic_name: str):
        return self.topics.get(topic_name, None)

    def list_subscriptions(self, topic: str):
        if topic in self.topics:
            return self.topics[topic]['subscriptions']
        return []

    def subscribe(self, topic_name: str, protocol: str, endpoint: str) -> Dict:
        if topic_name in self.topics:
            topic = self.topics[topic_name]
            if not self.subscription_exists(topic_name, endpoint):
                topic['subscriptions'].append({
                    "Endpoint": endpoint,
                    "Protocol": protocol
                })
                return {}
        return {}

    def publish(
        self,
        topic_name: str,
        payload: Union[Dict, str],
        attrs: Optional[Dict] = None,
    ) -> Dict:
        "Use this method to publish a message to a topic, it will return an empty dict if the message was published successfully."
        self.get_or_create_topic(topic_name)
        attrs = attrs or {}
        self.topics[topic_name]['messages'].append({
            "Message": payload,
            "Attributes": attrs
        })
        return {}

    def publish_batch(
        self,
        topic_name: str,
        payloads: List[Union[Dict, BaseModel]],
        attrs: Dict | None = ...
    ) -> List[Dict]:
        "Use this method to publish a batch of messages to a topic, it will return an empty dict if the messages were published successfully."
        self.get_or_create_topic(topic_name)
        for payload in payloads:
            self.topics[topic_name]['messages'].append({
                "Message": payload,
                "Attributes": attrs
            })
        return []

    def clear(self):
        self.topics = {}

    def topic_exists(self, topic_name: str) -> bool:
        return topic_name in self.topics

    def messages(self, topic_name: str) -> List[Dict]:
        messages = []
        for message in self.topics[topic_name]['messages']:
            m = message['Message']
            if isinstance(m, str):
                messages.append(m)
            if isinstance(m, dict):
                messages.append(m)
        return messages

    def attributes(self, topic_name: str) -> List[Dict]:
        messages = []
        for message in self.topics[topic_name]['messages']:
            m = message['Attributes']
            if isinstance(m, str):
                messages.append(m)
            if isinstance(m, dict):
                messages.append(m)
        return messages
