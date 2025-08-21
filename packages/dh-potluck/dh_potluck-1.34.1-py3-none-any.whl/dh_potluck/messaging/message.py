from datetime import datetime
from typing import TypedDict

from confluent_kafka.cimpl import Message as KafkaMessage


class MessageValue(TypedDict):
    message_type: str
    message_time: datetime
    payload: str


class Message(object):
    _topic: str
    _value: MessageValue
    _raw_message: KafkaMessage

    def __init__(self, topic: str, value: MessageValue, raw_message: KafkaMessage):
        """
        :param topic: The topic the message came from
        :param value: The message value
        :param raw_message: The raw kafka message object
        """
        self._topic = topic
        self._value = value
        self._raw_message = raw_message

    def topic(self) -> str:
        return self._topic

    def value(self) -> MessageValue:
        return self._value

    def raw_message(self) -> KafkaMessage:
        return self._raw_message
