from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email, db):
    """
    The get_user_by_email function takes in an email and a database connection.
    It then queries the User table for a user with that email address, returning the first result.

    :param email: Find the user in the database
    :param db: Connect to the database
    :return: The user object associated with the email address passed in
    :doc-author: Trelent
    """
    user = db.query(User).filter(User.email == email).first()
    return user


async def get_user_by_id(userid, db):
    """
    The get_user_by_id function takes in a userid and a database connection,
    and returns the User object associated with that id. If no such user exists,
    it returns None.

    :param userid: Filter the query to only return a user with that id
    :param db: Query the database for a user with the given id
    :return: A user object from the database
    :doc-author: Trelent
    """
    user = db.query(User).filter(User.id == userid).first()
    return user


async def add_user(body: UserModel, db):
    """
    The add_user function creates a new user in the database.

    :param body: UserModel: Define the type of data that is expected to be passed into this function
    :param db: Pass in the database connection
    :return: A user object
    :doc-author: Trelent
    """
    user = User(
        username=body.username,
        email=body.email,
        password=body.password,
        avatar=Gravatar(body.email).get_image()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


async def update_token(user: User, refresh_token, db: Session):
    """
    The update_token function updates the refresh token for a user in the database.
    Args:
    user (User): The User object to update.
    refresh_token (str): The new refresh token to store in the database.
    db (Session): A connection to our Postgres database.

    :param user: User: Identify the user that is being updated
    :param refresh_token: Update the user's refresh token in the database
    :param db: Session: Access the database
    :return: The user object
    :doc-author: Trelent
    """
    user.refresh_token = refresh_token
    db.commit()


async def update_reset_token(user: User, reset_token: str, db: Session):
    """
    The update_reset_token function updates the password reset token for a user.
    Args:
    user (User): The User object to update.
    reset_token (str): The new password reset token to set for the user.
    db (Session): A database session instance.

    :param user: User: Identify the user that needs to have their password reset
    :param reset_token: str: Set the password_reset_token field in the user table
    :param db: Session: Pass a database session to the function
    :return: A user
    :doc-author: Trelent
    """
    user.password_reset_token = reset_token
    db.commit()

async def update_password(user: User, new_password: str, db: Session):
    """
    The update_password function takes in a user object, a new password string, and the database session.
    It then updates the user's password to be equal to the new_password string.

    :param user: User: Pass in the user object
    :param new_password: str: Pass in the new password that the user wants to change it to
    :param db: Session: Access the database
    :return: None
    :doc-author: Trelent
    """
    user.password = new_password
    db.commit()


async def verify_email(user: User, db: Session):
    """
    The verify_email function takes in a user and database session,
    and sets the email_confirm field to True.


    :param user: User: Pass the user object to the function
    :param db: Session: Pass the database session to the function
    :return: A boolean value
    :doc-author: Trelent
    """
    user.email_confirm = True
    db.commit()


async def update_avatar(user: User, url: str, db: Session) -> User:
    """
    The update_avatar function updates the avatar of a user.

    :param user: User: Pass the user object to the function
    :param url: str: Pass in the url of the avatar to be updated
    :param db: Session: Pass the database session to the function
    :return: The user object
    :doc-author: Trelent
    """
    user.avatar = url
    db.commit()
    return user
