from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import Mapped, mapped_column

from tp_helper.functions import timestamp


class BaseTimestampModel:
    updated_at: Mapped[int] = mapped_column(
        INTEGER(unsigned=True),
        default=timestamp,
        onupdate=timestamp,
        nullable=False
    )

    created_at: Mapped[int] = mapped_column(
        INTEGER(unsigned=True),
        default=timestamp,
        nullable=False
    )
