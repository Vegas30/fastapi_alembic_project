from sqlmodel import Field, Relationship, SQLModel

from app.models.membership import Membership

class Project(SQLModel, table=True):
    __tablename__ = "projects"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)

    memberships: list["Membership"] = Relationship(back_populates="project")