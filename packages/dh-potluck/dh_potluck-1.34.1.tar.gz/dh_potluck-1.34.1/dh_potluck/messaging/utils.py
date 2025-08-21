from typing import Optional

from flask import current_app

from dh_potluck.messaging.constants import BROKER_LIST_CONFIG_KEY, USE_SSL_CONFIG_KEY
from dh_potluck.messaging.exceptions import NoBrokersFoundException
from dh_potluck.messaging.typings import ConsumerConfig


def build_consumer_config(
    consumer_group_id: str,
    config_overrides: Optional[ConsumerConfig] = None,
    brokers: Optional[str] = None,
    should_connect_ssl: Optional[bool] = None,
) -> ConsumerConfig:
    if brokers is None:
        brokers = current_app.config[BROKER_LIST_CONFIG_KEY]
    if not brokers:
        raise NoBrokersFoundException(
            'Tried to instantiate a MessageConsumer without providing '
            f'brokers or setting the {BROKER_LIST_CONFIG_KEY} env var'
        )

    config: ConsumerConfig = {
        'bootstrap.servers': brokers,
        'group.id': consumer_group_id,
        'enable.auto.commit': False,
        'auto.offset.reset': 'earliest',
    }

    if should_connect_ssl is None:
        should_connect_ssl = current_app.config.get(USE_SSL_CONFIG_KEY)
    if should_connect_ssl:
        config['security.protocol'] = 'SSL'
    if config_overrides:
        config.update(config_overrides)
    return config
