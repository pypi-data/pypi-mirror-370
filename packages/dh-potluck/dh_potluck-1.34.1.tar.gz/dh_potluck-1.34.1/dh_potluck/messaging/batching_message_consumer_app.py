import re
from functools import wraps
from json import JSONDecodeError
from typing import Any, Callable, Dict, List, Optional, Pattern, Tuple, Union

from ddtrace import tracer
from marshmallow import Schema, ValidationError

from dh_potluck.messaging import Message
from dh_potluck.messaging.batching_consumer import BatchingMessageConsumer
from dh_potluck.messaging.typings import BatchingMessagesHandler, MessageFilterFunction


class NoBatchingHandlerException(Exception):
    def __init__(self, topic, message_type, available_handlers):
        self.key = (topic, message_type)
        self.topic = topic
        self.message_type = message_type
        self.message = (
            f'No batching handler for: {topic=} {message_type=}. '
            f'Available handlers: {available_handlers}'
        )
        super().__init__(self.message)


class BatchingMessageConsumerApp:
    _consumer: BatchingMessageConsumer
    _handlers: Dict[Tuple[str, Optional[str]], BatchingMessagesHandler]
    _regex_handlers: Dict[Pattern[str], BatchingMessagesHandler]

    def __init__(self, batching_consumer: BatchingMessageConsumer):
        self._consumer = batching_consumer
        self._handlers = {}
        self._regex_handlers = {}

    def register(
        self,
        topic: str,
        message_type: Optional[str] = None,
        message_filter: Optional[MessageFilterFunction] = None,
    ) -> Callable[[BatchingMessagesHandler], BatchingMessagesHandler]:
        def decorator_register_message_handler(func: BatchingMessagesHandler):
            if message_filter is not None:
                self._consumer.add_message_filter(topic, message_type, message_filter)
            self.register_handler(topic, message_type, func)
            return func

        return decorator_register_message_handler

    def register_handler(self, topic, message_type, handler: BatchingMessagesHandler) -> None:
        # regexes must start with ^ for kafka to pick up on them
        if topic.startswith('^'):
            self._regex_handlers[re.compile(topic)] = handler
        else:
            self._handlers[(topic, message_type)] = handler

    def run(self) -> None:
        """
        Start consuming messages.
        """
        topics = [topic for topic, _ in self._handlers]
        topic_regexes = [regex.pattern for regex in self._regex_handlers]
        self._consumer.subscribe(set(topics + topic_regexes))
        for batch in self._consumer.get_batches():
            self._handle_batch(batch)

    def _handle_batch(self, batch: List[Message]) -> None:
        batches_by_topic_and_type: Dict[Tuple[str, str], List[Message]] = {}
        for message in batch:
            topic = message.topic()
            message_type = message.value()['message_type']
            batches_by_topic_and_type.setdefault((topic, message_type), []).append(message)

        for (topic, message_type), messages in batches_by_topic_and_type.items():
            should_commit = self._handle_one_topic_batch(topic, message_type, messages)
            if not self._consumer.auto_commit and should_commit:
                self._consumer.commit(messages=messages)

    def _handle_one_topic_batch(
        self,
        topic: str,
        message_type: str,
        messages: List[Message],
    ) -> bool:
        with tracer.trace('kafka.batch_consume', resource=f'{topic} {message_type}') as span:
            handler = self._get_handler(topic, message_type)
            span.set_tag('batch_size', len(messages))
            should_commit = handler(topic, message_type, messages)
            return should_commit is not False

    def _get_handler(self, topic: str, message_type: str) -> BatchingMessagesHandler:
        handler = self._handlers.get((topic, message_type))

        if not handler:
            handler = self._handlers.get((topic, None))

        if not handler:
            for topic_regex, _handler in self._regex_handlers.items():
                if topic_regex.match(topic):
                    handler = _handler
                    break

        if not handler:
            raise NoBatchingHandlerException(topic, message_type, list(self._handlers))
        return handler


def validate_schema_per_message(schema: Schema):
    def _wrapper(handler: Callable[[str, str, List[Any], List[Message]], Optional[bool]]):
        @wraps(handler)
        def wrapper(topic: str, message_type: str, messages: List[Message]) -> Optional[bool]:
            payloads = [schema.loads(message.value()['payload']) for message in messages]
            return handler(topic, message_type, payloads, messages)

        return wrapper

    return _wrapper


def validate_schemas_per_message(schemas: Dict[Tuple[str, str], Schema]):
    def _wrapper(handler: Callable[[str, str, List[Any], List[Message]], Optional[bool]]):
        @wraps(handler)
        def wrapper(topic: str, message_type: str, messages: List[Message]) -> Optional[bool]:
            schema = schemas.get((topic, message_type))
            if not schema:
                raise ValidationError(
                    f'No schema for topic {topic} and message_type {message_type}'
                )
            payloads = [schema.loads(message.value()['payload']) for message in messages]
            return handler(topic, message_type, payloads, messages)

        return wrapper

    return _wrapper


def validate_schema_per_message_and_ignore_errors(schema: Schema):
    def _wrapper(
        handler: Callable[
            [str, str, List[Any], List[Union[ValidationError, JSONDecodeError]], List[Message]],
            Optional[bool],
        ]
    ):
        @wraps(handler)
        def wrapper(topic: str, message_type: str, messages: List[Message]) -> Optional[bool]:
            payloads = []
            errors = []
            for message in messages:
                try:
                    payloads.append(schema.loads(message.value()['payload']))
                except (ValidationError, JSONDecodeError) as e:
                    errors.append(e)
            return handler(topic, message_type, payloads, errors, messages)

        return wrapper

    return _wrapper


def validate_schemas_per_message_and_ignore_errors(
    schemas: Dict[Tuple[str, Optional[str]], Schema]
):
    def _wrapper(
        handler: Callable[
            [str, str, List[Any], List[Union[ValidationError, JSONDecodeError]], List[Message]],
            Optional[bool],
        ]
    ):
        @wraps(handler)
        def wrapper(topic: str, message_type: str, messages: List[Message]) -> Optional[bool]:
            payloads = []
            errors = []
            schema = schemas.get((topic, message_type))
            if not schema:
                schema = schemas.get((topic, None))
            for message in messages:
                try:
                    if not schema:
                        raise ValidationError(
                            f'No schema for topic {topic} and message_type {message_type}'
                        )
                    payloads.append(schema.loads(message.value()['payload']))
                except (ValidationError, JSONDecodeError) as e:
                    errors.append(e)
            return handler(topic, message_type, payloads, errors, messages)

        return wrapper

    return _wrapper
