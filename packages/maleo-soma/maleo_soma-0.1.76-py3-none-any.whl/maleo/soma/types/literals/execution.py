from typing import Literal, Optional
from maleo.soma.enums.execution import Execution

SyncExecutionLiteral = Literal[Execution.SYNC]

OptionalSyncExecutionLiteral = Optional[SyncExecutionLiteral]

AsyncExecutionLiteral = Literal[Execution.ASYNC]

OptionalAsyncExecutionLiteral = Optional[AsyncExecutionLiteral]

ExecutionLiteral = Literal[Execution.SYNC, Execution.ASYNC]

OptionalExecutionLiteral = Optional[ExecutionLiteral]
