from spryx_http import AuthStrategy, SpryxAsyncClient

from spryx_message.resources.channels import Channels
from spryx_message.resources.contacts import Contacts
from spryx_message.resources.files import Files
from spryx_message.resources.messages import Messages


class SpryxMessage(SpryxAsyncClient):
    def __init__(
        self,
        base_url: str,
        auth_strategy: AuthStrategy,
    ):
        super().__init__(
            base_url=base_url,
            auth_strategy=auth_strategy,
        )

        self.channels = Channels(self)
        self.contacts = Contacts(self)
        self.files = Files(self)
        self.messages = Messages(self) 