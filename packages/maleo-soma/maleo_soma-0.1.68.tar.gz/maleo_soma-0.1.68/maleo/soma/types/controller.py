from google.cloud.pubsub_v1.subscriber.message import Message
from typing import Awaitable, Callable, Optional, Union

# * Message controller types
SyncMessageController = Callable[[str, Message], bool]
AsyncMessageController = Callable[[str, Message], Awaitable[bool]]
MessageController = Union[SyncMessageController, AsyncMessageController]
OptionalMessageController = Optional[MessageController]
