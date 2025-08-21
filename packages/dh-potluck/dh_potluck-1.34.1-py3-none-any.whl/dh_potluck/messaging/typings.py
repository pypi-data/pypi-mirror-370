from typing import Any, Callable, Dict, List, Optional

from dh_potluck.messaging import Message

# See: https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
# Cannot use a TypedDict easily here, see: https://github.com/python/mypy/issues/6462
ConsumerConfig = Dict[str, Any]

BatchingMessagesHandler = Callable[[str, str, List[Message]], Optional[bool]]

MessageFilterFunction = Callable[[str, str, Dict[str, Any]], bool]
