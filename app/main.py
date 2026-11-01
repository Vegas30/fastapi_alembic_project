from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.membership import Membership
from app.models.project import Project
from app.models.user import User

app = FastAPI(title="Alembic Practic API")

class UserCreate(BaseModel):
    email: str
    full_name: str | None = None


class UserRead(BaseModel):
    id: int
    email: str
    full_name: str | None = None
    model_config = {"from_attributes": True}

class ProjectCreate(BaseModel):
    title: str


class ProjectRead(BaseModel):
    id: int
    title: str
    model_config = {"from_attributes": True}

class JoinRequest(BaseModel):
    user_id: int
    role: str = "member"

class MemberRead(BaseModel):
    id: int
    user_id: int
    project_id: int
    role: str
    status: str
    email: str | None = None
    model_config = {"from_attributes": True}

@app.post("/users", response_model=UserRead, status_code=201)
def create_user(body: UserCreate, session: Session = Depends(get_session)):
    user = User(email=body.email, full_name=body.full_name)
    session.add(user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="User with this email already exists")
    session.refresh(user)
    return user



@app.post("/projects", response_model=ProjectRead, status_code=201)
def create_project(body: ProjectCreate, session: Session = Depends(get_session)):
    project = Project(title=body.title)
    session.add(project)
    session.commit()
    session.refresh(project)
    return project

@app.post("/projects/{project_id}/join", response_model=MemberRead, status_code=201)
def join_project(
    project_id: int,
    body: JoinRequest,
    session: Session = Depends(get_session),
):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    user = session.get(User, body.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if body.role not in ("member", "admin"):
        raise HTTPException(status_code=400, detail="role must be 'member' or 'admin'")

    membership = Membership(
        user_id=body.user_id,
        project_id=project_id,
        role=body.role,
        status="active",
    )
    session.add(membership)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="User is already a member of this project")

    session.refresh(membership)
    return MemberRead(
        id=membership.id,
        user_id=membership.user_id,
        project_id=membership.project_id,
        role=membership.role,
        status=membership.status,
        email=user.email,
    )


@app.get("/projects/{project_id}/members", response_model=list[MemberRead])
def list_members(project_id: int, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    statement = (
        select(Membership, User.email)
        .join(User, Membership.user_id == User.id)
        .where(Membership.project_id == project_id)
    )
    results = session.exec(statement).all()
    return [
        MemberRead(
            id=m.id,
            user_id=m.user_id,
            project_id=m.project_id,
            role=m.role,
            status=m.status,
            email=email,
        )
        for m, email in results
    ]