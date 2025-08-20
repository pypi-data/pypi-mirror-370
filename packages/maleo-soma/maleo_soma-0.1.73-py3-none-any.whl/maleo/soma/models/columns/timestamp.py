from sqlalchemy import Column, TIMESTAMP, func


class CreateTimestamp:
    created_at = Column(
        name="created_at",
        type_=TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class UpdateTimestamp:
    updated_at = Column(
        name="updated_at",
        type_=TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class LifecyleTimestamp(UpdateTimestamp, CreateTimestamp):
    pass


class DeleteTimestamp:
    deleted_at = Column(name="deleted_at", type_=TIMESTAMP(timezone=True))


class RestoreTimestamp:
    restored_at = Column(name="restored_at", type_=TIMESTAMP(timezone=True))


class DeactivateTimestamp:
    deactivated_at = Column(name="deactivated_at", type_=TIMESTAMP(timezone=True))


class ActivateTimestamp:
    activated_at = Column(
        name="activated_at",
        type_=TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class StatusTimestamp(
    ActivateTimestamp, DeactivateTimestamp, RestoreTimestamp, DeleteTimestamp
):
    pass


class DataTimestamp(StatusTimestamp, LifecyleTimestamp):
    pass
