from enum import Enum
from typing import Any, Dict, List, Literal, Optional, TypedDict, Union

from flask import current_app
from mailchimp_transactional import Client


class MandrillMergeLanguage(Enum):
    """
    Enum for templating languages supported by mailchimp.
    'mailchimp' is the default in Mandrill
    """

    MAILCHIMP = 'mailchimp'
    HANDLEBARS = 'handlebars'


MandrillRecipientType = Union[Literal['to'], Literal['cc'], Literal['bcc']]


class MandrillRecipient(TypedDict):
    email: str
    name: str
    type: MandrillRecipientType


class MandrillEmailClient:
    _DEFAULT_EMAIL_PROPS = {
        'from_name': 'Dash Social',
        'from_email': 'noreply@dashsocial.com',
        'track_clicks': True,
        'track_opens': True,
        'inline_css': True,
    }

    _client: Client

    def __init__(self):
        self._client = Client(current_app.config['DH_POTLUCK_MANDRILL_API_KEY'])

    def send_email_template(
        self,
        recipients: List[MandrillRecipient],
        template_name: str,
        template_vars: List[Dict[str, str]],
        subject: Optional[str] = None,
        merge_language: Optional[MandrillMergeLanguage] = None,
        template_vars_overrides_for_recipients: Optional[List[Dict[str, Any]]] = None,
        preserve_recipients: bool = True,
    ) -> None:
        message = {
            'track_clicks': self._DEFAULT_EMAIL_PROPS['track_clicks'],
            'track_opens': self._DEFAULT_EMAIL_PROPS['track_opens'],
            'from_name': self._DEFAULT_EMAIL_PROPS['from_name'],
            'from_email': self._DEFAULT_EMAIL_PROPS['from_email'],
            'to': recipients,
            'global_merge_vars': template_vars,
            'preserve_recipients': preserve_recipients,
        }
        if subject:
            message['subject'] = subject

        if merge_language:
            message['merge_language'] = merge_language.value

        if template_vars_overrides_for_recipients:
            message['merge_vars'] = template_vars_overrides_for_recipients

        self._client.messages.send_template(
            {
                'template_name': template_name,
                'message': message,
                'template_content': [],
            }
        )

    def send_email_html(
        self,
        recipients: List[MandrillRecipient],
        subject: Optional[str] = None,
        html: Optional[str] = None,
        preserve_recipients: bool = True,
    ) -> None:
        message = {
            'track_clicks': self._DEFAULT_EMAIL_PROPS['track_clicks'],
            'track_opens': self._DEFAULT_EMAIL_PROPS['track_opens'],
            'from_name': self._DEFAULT_EMAIL_PROPS['from_name'],
            'from_email': self._DEFAULT_EMAIL_PROPS['from_email'],
            'inline_css': self._DEFAULT_EMAIL_PROPS['inline_css'],
            'to': recipients,
            'preserve_recipients': preserve_recipients,
        }
        if html:
            message['html'] = html

        if subject:
            message['subject'] = subject

        self._client.messages.send({'message': message})
