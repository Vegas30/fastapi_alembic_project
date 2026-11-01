from datetime import datetime, timezone

from sqlmodel import Field, SQLModel, Relationship 

from app.models.membership import Membership

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    full_name: str | None = Field(default=None)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": "now()"}
    )

    memberships: list["Membership"] = Relationship(back_populates="user")


#GENERATOR, Декаратор
#default_factory=lambda: datetime.now(timezone.utc),
    #     sa_column_kwargs={"server_default": "now()"}
    # )