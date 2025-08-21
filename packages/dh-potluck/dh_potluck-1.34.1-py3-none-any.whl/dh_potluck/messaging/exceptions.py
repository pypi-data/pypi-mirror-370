from confluent_kafka import KafkaException


class CommitTimeoutException(KafkaException):
    pass


class NoBrokersFoundException(RuntimeError):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)
