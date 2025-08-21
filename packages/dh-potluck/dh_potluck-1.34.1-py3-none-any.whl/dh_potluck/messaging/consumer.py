import logging
from typing import Iterable, Iterator, Optional

from confluent_kafka import Consumer

from dh_potluck.messaging import Message, MessageEnvelopeSchema
from dh_potluck.messaging.typings import ConsumerConfig
from dh_potluck.messaging.utils import build_consumer_config

LOG = logging.getLogger(__name__)


class MessageConsumer(object):

    _consumer: Consumer
    _is_consuming: bool = False
    _message_schema: MessageEnvelopeSchema = MessageEnvelopeSchema()

    def __init__(
        self,
        consumer_group_id: str,
        config_overrides: Optional[ConsumerConfig] = None,
        brokers: Optional[str] = None,
        should_connect_ssl: Optional[bool] = None,
    ):
        """
        :param str consumer_group_id: The kafka consumer group to use
        :param dict config_overrides: Any kafka configuration overrides
        :param str brokers: list of brokers to connect to (also can be provided via the flask
            config `KAFKA_BROKERS_LIST`)
        :param bool should_connect_ssl: if a ssl connection should be used to kafka (also can be
            provided via the flask config `KAFKA_USE_SSL_CONNECTION`)
        """
        self._consumer = Consumer(
            build_consumer_config(consumer_group_id, config_overrides, brokers, should_connect_ssl)
        )

    def subscribe(self, topics: Iterable[str]) -> None:
        """
        Subscribe to the list of topics, this makes the connection to Kafka
        :param topics: Topics to connect to
        :return: None
        """
        self._consumer.subscribe(list(topics))

    def get_messages(self, poll_timeout: float = 1.0) -> Iterator[Message]:
        """
        Get messages from topics

        :param float poll_timeout: Maximum time to block waiting for message. (Seconds)
        :return: Iterator[Message]
        """
        self._is_consuming = True
        while self._is_consuming:
            message = self._consumer.poll(poll_timeout)

            if message is None:
                continue
            if message.error():
                LOG.error(f'Consumer error: {message.error()}')
                continue

            message_value_string = message.value().decode('utf-8')
            LOG.debug(f'Received message: {message_value_string}')
            message_value = self._message_schema.loads(message_value_string)
            yield Message(message.topic(), message_value, message)

    def commit(self, message: Message) -> None:
        """
        Commit the message, this is done after successfully processing the message

        :param Message message: Message to commit
        :return: None
        """
        self._consumer.commit(message.raw_message())

    def shutdown(self) -> None:
        """
        Call when service is shutting down

        :return: None
        """
        LOG.info('Consumer shutting down...')
        self._is_consuming = False
        if self._consumer:
            self._consumer.close()
        LOG.info('Consumer shut down')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()
