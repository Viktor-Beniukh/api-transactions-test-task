import logging

from fastapi import APIRouter, status, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from src.core.database import models
from src.core.database.db_settings.db_helper import db_dependency

from src.repositories import admin as repository_admin
from src.schemas.admin import AdminResponse, AdminRegister, AdminMessageResponse
from src.services.auth_dependencies import get_current_admin

from src.services.security import verify_password


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])

templates = Jinja2Templates(directory="templates")


@router.post("/register",
             response_model=AdminResponse,
             status_code=status.HTTP_201_CREATED)
async def create_admin(admin: AdminRegister, session: db_dependency) -> models.User:
    """
    The create_admin function creates an admin in the database.
        It takes an AdminRegister object as input, and returns the newly created admin.

        Args:
            admin: AdminRegister: Receive the data of the user to be created
            session: db_dependency: Access the database

    Returns:
        The created admin
    """
    admin_username = await repository_admin.get_admin_by_username(username=admin.username, session=session)

    if admin_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Admin already exists",
        )

    new_admin = await repository_admin.register_admin(admin=admin, session=session)

    return new_admin


@router.post("/login")
async def login_admin(
    session: db_dependency, form_data: OAuth2PasswordRequestForm = Depends(),
) -> dict[str, str]:
    """
    The login_admin function is used to receive the authentication token.
        The function takes in the user credentials and returns an authentication token

        Arguments:
            form_data(OAuth2PasswordRequestForm): enter the user credentials
            session (db_dependency): SQLAlchemy session object for accessing the database

    Returns:
        dict: the authentication token
    """

    admin = await repository_admin.get_admin_by_username(username=form_data.username, session=session)

    if admin is None or not verify_password(
        plain_password=form_data.password, hashed_password=admin.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid username or password"
        )

    token = await repository_admin.login_admin(
        username=form_data.username, password=form_data.password, session=session
    )

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate token"
        )

    return {"token": token}


@router.post("/logout", response_model=AdminMessageResponse, dependencies=[Depends(get_current_admin)])
async def logout_admin(session: db_dependency) -> dict[str, str]:
    """
    The logout_admin function is used to log out an admin user.
        The function revokes the authentication token of the admin user

        Arguments:
            session (db_dependency): SQLAlchemy session object for accessing the database

    Returns:
        Message about successfully logged out
    """

    await repository_admin.logout_admin(session=session)

    return {"message": "Successfully logged out"}


@router.get("/admin_panel", response_class=HTMLResponse, dependencies=[Depends(get_current_admin)])
async def admin_panel(request: Request):
    data = {"message": "Welcome to the Admin Panel!"}
    return templates.TemplateResponse("admin_panel.html", {"request": request, "data": data})
