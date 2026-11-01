from typing import TYPE_CHECKING

from sqlmodel import (
    CheckConstraint,
    Field,
    Relationship,
    SQLModel,
    UniqueConstraint,
)

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.user import User

class Membership(SQLModel, table=True):
    __tablename__ = "memberships"
    __table_args__ = (
        UniqueConstraint("user_id", "project_id"),
        # Check constraints are named explicitly — see models/__init__.py for why
        CheckConstraint("role IN ('member', 'admin')", name="ck_memberships_role"),
    )

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    project_id: int = Field(foreign_key="projects.id")
    role: str = Field(default="member")
    status: str = Field(default="active", nullable=False)

    user: "User" = Relationship(back_populates="memberships")
    project: "Project" = Relationship(back_populates="memberships")



#user -> 1  
#project -> 1 
#project -> 2
#membership -> 1 1 member active 
#membership -> 1 1 member admin
#membership -> 1 2 member active


#membership.user -> 1 user (всю информацию о пользователе)
#membership.project (1) -> 1 project (всю информацию о проекте)