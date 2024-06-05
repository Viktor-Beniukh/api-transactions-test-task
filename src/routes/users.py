from fastapi import APIRouter, status, HTTPException

from src.core.database import models
from src.core.database.db_settings.db_helper import db_dependency

from src.repositories import users as repository_users
from src.repositories import transactions as repository_transactions

from src.schemas.transactions import (
    TransactionPartialUpdate,
    TransactionMessageResponse,
    TransactionResponse,
    TransactionCreate,
)
from src.schemas.users import UserResponse, UserCreate, UserUpdate

router = APIRouter(tags=["Users"])


@router.post("/",
             response_model=UserResponse,
             status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, session: db_dependency) -> models.User:
    """
    The create_user function creates a new user in the database.

        Args:
            user_data: UserCreate: Validate the request body
            session: db_dependency: Pass the database session to the repository layer

    Returns:
        A user object
    """
    user = await repository_users.get_user_by_username(
        session=session, username=user_data.username
    )

    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="The username of the user already exists"
        )

    return await repository_users.create_user(user=user_data, session=session)


@router.get("/", response_model=list[UserResponse])
async def get_all_users(session: db_dependency) -> list[models.User]:
    """
    The function returns a list of all users in the database.

        Args:
            session: db_dependency: Access the database

    Returns:
        A list of users
    """

    users = await repository_users.get_all_users(session=session)

    if len(users) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Users not found")

    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_single_user(user_id: int, session: db_dependency) -> models.User:
    """
    The function returns the single user data in the database.

        Args:
            user_id: int: int: Get the id of the user to be obtained
            session: db_dependency: Access the database

    Returns:
        The user object
    """

    user = await repository_users.get_user_by_id_with_transactions(user_id=user_id, session=session)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


@router.put("/{user_id}/update", response_model=UserResponse)
async def update_user(updated_user: UserUpdate, user_id: int, session: db_dependency) -> models.User:
    """
    The update_user function is used to update the user.
        The function takes in the id of the user to be updated.

        Args:
            updated_user: UserUpdate: Validate the request body
            user_id: int: Get the id of the user to be updated
            session: db_dependency: Access the database

    Returns:
        The user object
    """
    user = await repository_users.get_user_by_id(user_id=user_id, session=session)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    updated_user_data = await repository_users.update_user(
        user_update=updated_user, user_id=user.id, session=session
    )

    return updated_user_data


@router.delete("/{user_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, session: db_dependency) -> None:
    """
    The delete_user function is used to delete the user.
        The function takes in the id of the user to be unarchived.

        Args:
            user_id: int: Get the id of the user to be deleted
            session: db_dependency: Access the database

    Returns:
        None
    """
    user = await repository_users.get_user_by_id(user_id=user_id, session=session)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.transactions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User has some transactions. Operation forbidden!"
        )

    await repository_users.delete_user(user_id=user.id, session=session)


@router.post("/{user_id}/transactions/create",
             response_model=TransactionResponse,
             status_code=status.HTTP_201_CREATED)
async def add_transaction_for_user(
    transaction_data: TransactionCreate,
    user_id: int,
    session: db_dependency
) -> models.Transaction:
    """
    The create_user function creates a new user in the database.

        Args:
            transaction_data: TransactionCreate: Validate the request body
            user_id: int: Get the id of the user to create a transaction
            session: db_dependency: Pass the database session to the repository layer

    Returns:
        A transaction object
    """

    return await repository_transactions.create_transaction(
        transaction=transaction_data, user_id=user_id, session=session)


@router.patch("/{user_id}/transactions/{transaction_id}/partial_update",
              response_model=TransactionMessageResponse)
async def partial_update_transaction(
    updated_transaction: TransactionPartialUpdate,
    user_id: int,
    transaction_id: int,
    session: db_dependency
) -> dict[str, str]:
    """
    The partial_update_transaction function is used to update the transaction.
        The function takes in the id of the user and the transaction to be updated.

        Args:
            updated_transaction: TransactionPartialUpdate: Validate the request body
            user_id: int: Get the id of the user to update the transaction
            transaction_id: int: Get the id of the transaction to be updated
            session: db_dependency: Access the database

    Returns:
        Message about successful updating of transaction
    """

    await repository_transactions.partial_update_transaction(
        transaction_update=updated_transaction,
        transaction_id=transaction_id,
        user_id=user_id,
        session=session
    )

    return {"message": "The transaction updated successfully!"}


@router.delete("/{user_id}/transactions/{transaction_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(user_id: int, transaction_id: int, session: db_dependency) -> None:
    """
    The delete_transaction function is used to delete the transaction.
        The function takes in the id of the user and the id of the transaction to be deleted.

        Args:
            user_id: int: Get the id of the user to delete the transaction
            transaction_id: int: Get the id of the transaction to be deleted
            session: db_dependency: Access the database

    Returns:
        None
    """

    await repository_transactions.delete_transaction(
        user_id=user_id, transaction_id=transaction_id, session=session
    )
