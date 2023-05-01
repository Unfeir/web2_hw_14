from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, Depends, status
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import redis

from src.conf.config import settings
from src.database.db import get_db
from src.repository import user as repository_user


class AuthPassword:
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

    def get_hash_password(self, password: str):
        """
        The get_hash_password function takes a password as an argument and returns the hashed version of that password.
        The hash is generated using the pwd_context object's hash method, which uses bcrypt to generate a secure hash.

        :param self: Represent the instance of the class
        :param password: str: Get the password from the user
        :return: A hash of the password
        :doc-author: Trelent
        """
        return self.pwd_context.hash(password)

    def verify_password(self, password: str, hashed_password: str):
        """
        The verify_password function takes a plain-text password and hashed password as arguments.
        It then uses the verify method of the pwd_context object to check if they match.

        :param self: Make the function a method of the class
        :param password: str: Pass in the password that is being checked
        :param hashed_password: str: Compare the password to the hashed_password
        :return: A boolean value
        :doc-author: Trelent
        """
        return self.pwd_context.verify(password, hashed_password)


class AuthToken:
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/login')
    r = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        The create_access_token function creates a new access token.
        Args:
        data (dict): A dictionary containing the claims to be encoded in the JWT.
        expires_delta (Optional[float]): An optional timedelta of seconds for the expiration time of this token.

        :param self: Represent the instance of the class
        :param data: dict: Pass in the data that you want to encode into your token
        :param expires_delta: Optional[float]: Set the expiration time of the token
        :return: A string
        :doc-author: Trelent
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=30)

        to_encode.update({'iat': datetime.utcnow(), 'exp': expire, 'scope': 'access_token'})
        access_token = jwt.encode(to_encode, self.SECRET_KEY, self.ALGORITHM)
        return access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        The create_refresh_token function creates a refresh token for the user.
        Args:
        data (dict): A dictionary containing the user's id and username.
        expires_delta (Optional[float]): The amount of time in minutes until the token expires. Defaults to 30 minutes if not specified by caller.

        :param self: Represent the instance of the class
        :param data: dict: Pass the user's data to the function
        :param expires_delta: Optional[float]: Set the expiration time of the token
        :return: The refresh token
        :doc-author: Trelent
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=30)

        to_encode.update({'iat': datetime.utcnow(), 'exp': expire, 'scope': 'refresh_token'})
        refresh_token = jwt.encode(to_encode, self.SECRET_KEY, self.ALGORITHM)
        return refresh_token

    async def create_reset_password_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        The create_reset_password_token function creates a reset password token.
        Args:
        data (dict): A dictionary containing the user's email and username.
        expires_delta (Optional[float]): The time in minutes until the token expires. Defaults to 5 minutes if not specified.

        :param self: Make the function a method of the class
        :param data: dict: Pass in the data that will be encoded
        :param expires_delta: Optional[float]: Set the expiration time for the token
        :return: A reset_password_token
        :doc-author: Trelent
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=5)

        to_encode.update({'iat': datetime.utcnow(), 'exp': expire, 'scope': 'reset_password_token'})
        reset_password_token = jwt.encode(to_encode, self.SECRET_KEY, self.ALGORITHM)
        return reset_password_token

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        """
        The get_current_user function is a dependency that will be used in the
        get_current_active_user endpoint. It takes a token as an argument and
        returns the user id of the user associated with that token. If no such
        user exists, it raises an HTTPException.

        :param self: Refer to the class itself
        :param token: str: Get the token from the request header
        :param db: Session: Get the database session
        :return: The user id of the currently logged in user
        :doc-author: Trelent
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )

        try:
            payload = jwt.decode(token, self.SECRET_KEY, self.ALGORITHM)
            if payload['scope'] == 'access_token':
                email = payload['sub']
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except:
            raise credentials_exception
        user = self.r.get(email)
        if user is None:
            user = await repository_user.get_user_by_email(email, db)
            user = user.id
            if user is None:
                raise credentials_exception
            self.r.set(email, user)
            self.r.expire(email, 60)
        else:
            user = user.decode()
        return user

    async def refresh_token_email(self, refresh_token: str = Depends(oauth2_scheme)):
        """
        The refresh_token_email function is used to validate a refresh token and return the email of the user who owns it.
        This function is called by the /token/refresh endpoint, which returns a new access token for an authenticated user.

        :param self: Represent the instance of a class
        :param refresh_token: str: Get the refresh token from the authorization header
        :return: The email of the user who is logged in
        :doc-author: Trelent
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, self.ALGORITHM)
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                if email is None:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid Email')
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

        return email

    async def reset_token_email(self, reset_token: str = Depends(oauth2_scheme)):
        """
        The reset_token_email function is used to validate the reset password token.
        It will return the email of the user if it is valid, otherwise it will raise an HTTPException.

        :param self: Represent the instance of the class
        :param reset_token: str: Get the reset token from the url
        :return: The email of the user that is resetting their password
        :doc-author: Trelent
        """
        try:
            payload = jwt.decode(reset_token, self.SECRET_KEY, self.ALGORITHM)
            if payload['scope'] == 'reset_password_token':
                email = payload['sub']
                if email is None:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid Email')
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

        return email

    async def create_email_token(self, data: dict):
        """
        The create_email_token function takes in a dictionary of data and returns a token.
        The token is created using the JWT library, which encodes the data into a string that can be decoded later.
        The function also adds an expiration time to the encoded data.

        :param self: Represent the instance of the class
        :param data: dict: Pass in the data that will be encoded
        :return: A token that is encoded with the data, secret key and algorithm
        :doc-author: Trelent
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(hours=1)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
        """
        The get_email_from_token function takes a token as an argument and returns the email address associated with that token.
        The function uses the jwt library to decode the token, which is then used to return the email address.

        :param self: Represent the instance of the class
        :param token: str: Specify the token that is passed in the request body
        :return: The email address associated with the token
        :doc-author: Trelent
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")
