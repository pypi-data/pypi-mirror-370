from datetime import datetime
from sqlmodel import Field, SQLModel, BigInteger


class MessageLog(SQLModel, table=True):
    __tablename__ = "quickbot_agent_message_log"

    id: int = Field(
        primary_key=True,
        index=True,
        sa_type=BigInteger,
    )

    user_id: int = Field(
        index=True,
        sa_type=BigInteger,
    )

    is_business_chat: bool = Field(
        default=False,
    )

    client_id: int | None = Field(
        index=True,
        sa_type=BigInteger,
    )

    dt: datetime = Field(
        index=True,
        default_factory=datetime.now,
    )

    content: str
