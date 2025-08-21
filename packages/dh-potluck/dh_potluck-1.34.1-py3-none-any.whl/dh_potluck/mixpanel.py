from typing import Dict, Optional

from flask import current_app
from mixpanel import Mixpanel

from dh_potluck.types.json_serializable import JSONSerializable

MixpanelProperties = Optional[Dict[str, JSONSerializable]]


class MixpanelService:
    _mp: Mixpanel = None

    @classmethod
    def _get_mixpanel_client(cls):
        if not cls._mp:
            cls._mp = Mixpanel(current_app.config['DH_POTLUCK_MIXPANEL_TOKEN'])
        return cls._mp

    @classmethod
    def send_event(
        cls, user_id: str, event_name: str, properties: MixpanelProperties = None
    ) -> None:
        try:
            cls._get_mixpanel_client().track(user_id, event_name, properties)
        except Exception as e:
            raise MixpanelServiceException(
                message=f'Error occurred while sending mixpanel event: {str(e)}'
            )


class MixpanelServiceException(Exception):
    def __init__(self, message: str = 'Error occurred while sending mixpanel event.') -> None:
        self.message = message
        super().__init__(self.message)
