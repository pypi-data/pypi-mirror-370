from google.cloud.pubsub_v1.subscriber.message import Message
from typing import Awaitable, Callable, Optional, TypeVar, Union

# Message controller types
SyncMessageController = Callable[[str, Message], bool]
OptionalSyncMessageController = Optional[SyncMessageController]
AsyncMessageController = Callable[[str, Message], Awaitable[bool]]
OptionalAsyncMessageController = Optional[AsyncMessageController]
MessageController = Union[SyncMessageController, AsyncMessageController]
OptionalMessageController = Optional[MessageController]
MessageControllerT = TypeVar("MessageControllerT", bound=MessageController)
