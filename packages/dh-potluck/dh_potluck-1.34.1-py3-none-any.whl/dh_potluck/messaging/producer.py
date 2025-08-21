import logging
from datetime import datetime, timezone
from typing import Callable, Dict, Optional, Union

from confluent_kafka import Producer
from confluent_kafka.cimpl import KafkaError, KafkaException
from confluent_kafka.cimpl import Message as KafkaMessage
from ddtrace import tracer
from flask import current_app
from marshmallow import Schema, ValidationError

from dh_potluck.messaging import MessageEnvelopeSchema
from dh_potluck.messaging.constants import BROKER_LIST_CONFIG_KEY, USE_SSL_CONFIG_KEY
from dh_potluck.messaging.exceptions import NoBrokersFoundException

LOG = logging.getLogger(__name__)


class MessageProducer(object):

    _producer: Producer
    _message_schema: MessageEnvelopeSchema = MessageEnvelopeSchema()

    def __init__(
        self,
        config_overrides: Optional[Dict[str, object]] = None,
        brokers: Optional[str] = None,
        should_connect_ssl: Optional[bool] = None,
    ):
        """
        :param dict config_overrides: Any kafka configuration overrides
        :param str brokers: list of brokers to connect to (also can be provided via the flask
            config `KAFKA_BROKERS_LIST`)
        :param bool should_connect_ssl: if a ssl connection should be used to kafka (also can be
            provided via the flask config `KAFKA_USE_SSL_CONNECTION`)
        """
        if brokers is None:
            brokers = current_app.config[BROKER_LIST_CONFIG_KEY]
        if brokers is None:
            raise NoBrokersFoundException(
                'Tried to instantiate a MessageProducer without providing '
                f'brokers or setting the {BROKER_LIST_CONFIG_KEY} env var'
            )
        config: Dict[str, object] = {'bootstrap.servers': brokers}
        if should_connect_ssl is None:
            should_connect_ssl = current_app.config[USE_SSL_CONFIG_KEY]
        if should_connect_ssl:
            config['security.protocol'] = 'SSL'
        if config_overrides:
            config.update(config_overrides)
        self._producer = Producer(config)

    @staticmethod
    def _default_delivery_report(error: KafkaError, message: KafkaMessage) -> None:
        """Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush()."""
        if error is not None:
            LOG.error(f'Message delivery failed: {error}')
        else:
            LOG.debug(f'Message delivered to {message.topic()} [{message.partition()}]')

    def send_message(
        self,
        topic: str,
        message_type: str,
        payload: str,
        key: Optional[Union[str, bytes]] = None,
        on_delivery: Optional[Callable[[KafkaError, KafkaMessage], None]] = None,
        poll_timeout: float = 0,
    ) -> None:
        """
        Send a message

        :param str topic: Topic to send the message on
        :param str message_type: Message type
        :param str payload: Serialized message payload
        :param str|bytes key: (Optional) Message key, used to determine the partition the message
                              will go to
        :param func on_delivery: (Optional) Delivery report callback to call on successful or failed
                                 delivery
        :param float poll_timeout: Maximum time to block waiting for messages. (Seconds)
        :return: None
        :raises ValidationError: if the message doesn't conform to tge expected MessageSchema
        :raises BufferError: if the internal producer message queue is full
                             (``queue.buffering.max.messages`` exceeded)
        :raises KafkaException: for other errors, see exception code
        """
        LOG.debug(f'Sending message on topic {topic}')
        body = {
            'message_type': message_type,
            'message_time': datetime.now(timezone.utc),
            'payload': payload,
        }
        body_str = self._serialize(body, self._message_schema)
        try:
            with tracer.trace('kafka.produce', resource=f'{topic} {message_type}'):
                self._producer.produce(
                    topic,
                    body_str.encode('utf-8'),
                    key=key,
                    on_delivery=on_delivery or self._default_delivery_report,
                )
                self._producer.poll(poll_timeout)
        except BufferError as e:
            LOG.error(f'Message buffer is full!: {e}')
            raise e
        except KafkaException as e:
            LOG.error(f'Failed to send message to broker: {e}')
            raise e

    def send_message_with_schema(
        self,
        topic: str,
        message_type: str,
        payload: Dict[str, object],
        schema: Schema,
        key: Optional[Union[str, bytes]] = None,
        on_delivery: Optional[Callable[[KafkaError, KafkaMessage], None]] = None,
        poll_timeout: float = 0,
    ) -> None:
        """
        Send a message

        :param str topic: Topic to send the message on
        :param str message_type: Message type
        :param dict payload: Message payload
        :param Schema schema: Marshmallow schema to serialize payload
        :param str|bytes key: (Optional) Message key, used to determine the partition the message
                              will go to
        :param func on_delivery: (Optional) Delivery report callback to call on successful or failed
                                 delivery
        :param float poll_timeout: Maximum time to block waiting for messages. (Seconds)
        :return: None
        :raises ValidationError: if the message doesn't conform to tge expected MessageSchema
        :raises BufferError: if the internal producer message queue is full
                             (``queue.buffering.max.messages`` exceeded)
        :raises KafkaException: for other errors, see exception code
        """
        payload_str = self._serialize(payload, schema)

        self.send_message(
            topic=topic,
            message_type=message_type,
            payload=payload_str,
            key=key,
            on_delivery=on_delivery,
            poll_timeout=poll_timeout,
        )

    def _serialize(self, payload: Dict[str, object], schema: Schema) -> str:
        try:
            payload_str: str = schema.dumps(payload)
            schema.loads(payload_str)
        except ValidationError as e:
            LOG.error(f'Validation error(s) while sending message: {e}')
            raise e
        return payload_str

    def shutdown(self) -> None:
        """
        Call when service is shutting down
        :return: None
        """
        LOG.info('Producer shutting down...')
        if self._producer:
            self._producer.flush()
        LOG.info('Producer shut down')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()
