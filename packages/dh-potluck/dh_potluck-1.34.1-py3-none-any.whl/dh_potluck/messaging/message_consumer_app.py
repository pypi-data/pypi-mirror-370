import logging
import re
from functools import wraps
from json import JSONDecodeError
from typing import Any, Callable, Dict, Optional, Pattern, Protocol, Tuple, Union

from ddtrace import tracer
from marshmallow import Schema, ValidationError

from dh_potluck.messaging import Message, MessageConsumer

LOG = logging.getLogger(__name__)


class MessageHandlerCallback(Protocol):
    def __call__(self, topic: str, message_type: str, message: Message) -> bool:
        pass


class NoHandlerException(Exception):
    def __init__(self, topic, message_type):
        self.topic = topic
        self.message = f'No handler for topic: {topic}, message_type: {message_type}'
        super().__init__(self.message)


class MessageConsumerApp(object):

    _consumer: MessageConsumer
    _handlers: Dict[Tuple[str, Optional[str]], MessageHandlerCallback]
    _regex_handlers: Dict[Pattern[str], MessageHandlerCallback] = {}

    def __init__(self, consumer: MessageConsumer):
        """
        :param str consumer: MessageConsumer
        """
        self._consumer = consumer
        self._handlers = {}
        self._regex_handlers = {}

    def register(self, topic: str, message_type: Optional[str] = None):
        """
        Registers decorated function as a message handler
        :param str topic: Topic to handle, supports regex topics by prefixing with `^`
        :param Optional[str] message_type: Message Type to handle (Ignored for regex topics)
        """

        def decorator_register_message_handler(func: MessageHandlerCallback):
            self.register_handler(topic, message_type, func)
            return func

        return decorator_register_message_handler

    def register_handler(
        self,
        topic: str,
        message_type: Optional[str],
        handler: MessageHandlerCallback,
    ) -> None:
        # regexes must start with ^ for kafka to pick up on them
        if topic.startswith('^'):
            self._regex_handlers[re.compile(topic)] = handler
        else:
            self._handlers[(topic, message_type)] = handler

    def run(self):
        """
        Start consuming messages. On new messages, check the handlers map, if the message's topic
        and message_type matches a handler key, use it to serialize the message, and handle it.
        :return: None
        """
        topics = [topic for topic, _ in self._handlers]
        topic_regexes = [regex.pattern for regex in self._regex_handlers]
        self._consumer.subscribe(set(topics + topic_regexes))
        try:
            for message in self._consumer.get_messages():
                self._handle_message(message)
        finally:
            self._consumer.shutdown()

    def _handle_message(self, message: Message) -> None:
        topic = message.topic()
        message_type = message.value()['message_type']
        with tracer.trace('kafka.consume', resource=f'{topic} {message_type}'):
            handler = self._get_handler(topic, message_type)
            should_commit = handler(topic, message_type, message)
            if should_commit is not False:
                self._consumer.commit(message)

    def _get_handler(self, topic: str, message_type: str) -> MessageHandlerCallback:
        key: Tuple[str, Optional[str]] = (topic, message_type)
        handler = self._handlers.get(key)

        if not handler:
            key = (topic, None)
            handler = self._handlers.get(key)

        if not handler:
            for topic_regex, _handler in self._regex_handlers.items():
                if topic_regex.match(topic):
                    handler = _handler
                    break

        if not handler:
            raise NoHandlerException(topic, message_type)

        return handler


def validate_schema(schema: Schema):
    """
    Validate a message's schema

    :param Schema schema: schema to use when validating the message payload
    """

    def _wrapper(handler: Callable[[str, str, Any, Message], Optional[bool]]):
        @wraps(handler)
        def wrapper(topic: str, message_type: str, message: Message) -> Optional[bool]:
            payload = schema.loads(message.value()['payload'])
            return handler(topic, message_type, payload, message)

        return wrapper

    return _wrapper


def validate_schemas(schemas: Dict[Tuple[str, str], Schema]):
    """
    Validate a message's schema

    :param Dict[Tuple[str, str], Schema] schemas: mapping of topic and message_type to schema to use
        when validating the message payload
    """

    def _wrapper(handler: Callable[[str, str, Any, Message], Optional[bool]]):
        @wraps(handler)
        def wrapper(topic: str, message_type: str, message: Message) -> Optional[bool]:
            schema = schemas.get((topic, message_type))
            if not schema:
                raise ValidationError(
                    f'No schema for topic {topic} and message_type {message_type}'
                )
            payload = schema.loads(message.value()['payload'])
            return handler(topic, message_type, payload, message)

        return wrapper

    return _wrapper


def validate_schema_and_ignore_errors(schema: Schema):
    """
    Validate a message's schema, but catch errors and return them to the function

    This can be useful in some cases when skipping messages on schema errors is acceptable, but
    allowing schema issues to crash the consumer will prevent skipping messages and losing data.

    :param Schema schema: schema to use when validating the message payload
    """

    def _wrapper(
        handler: Callable[
            [str, str, Any, Union[ValidationError, JSONDecodeError, None], Message],
            Optional[bool],
        ]
    ):
        @wraps(handler)
        def wrapper(topic: str, message_type: str, message: Message) -> Optional[bool]:
            payload = None
            error = None
            try:
                payload = schema.loads(message.value()['payload'])
            except (ValidationError, JSONDecodeError) as e:
                error = e
            return handler(topic, message_type, payload, error, message)

        return wrapper

    return _wrapper


def validate_schemas_and_ignore_errors(schemas: Dict[Tuple[str, Optional[str]], Schema]):
    """
    Validate a message's schema, but catch errors and return them to the function

    This can be useful in some cases when skipping messages on schema errors is acceptable, but
    allowing schema issues to crash the consumer will prevent skipping messages and losing data.

    :param Dict[Tuple[str, str], Schema] schemas: mapping of topic and message_type to schema to use
        when validating the message payload
    """

    def _wrapper(
        handler: Callable[
            [str, str, Any, Union[ValidationError, JSONDecodeError, None], Message],
            Optional[bool],
        ]
    ):
        @wraps(handler)
        def wrapper(topic: str, message_type: str, message: Message) -> Optional[bool]:
            payload = None
            error = None
            schema = schemas.get((topic, message_type))
            if not schema:
                schema = schemas.get((topic, None))
            try:
                if not schema:
                    raise ValidationError(
                        f'No schema for topic {topic} and message_type {message_type}'
                    )
                payload = schema.loads(message.value()['payload'])
            except (ValidationError, JSONDecodeError) as e:
                error = e
            return handler(topic, message_type, payload, error, message)

        return wrapper

    return _wrapper
