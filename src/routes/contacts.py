from datetime import date
from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Path
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import ContactModel, ContactsResponse
from src.repository import contacts as repository_contacts
from src.services.auth import AuthToken

router = APIRouter(prefix='/contacts', tags=["contacts"])
authtoken = AuthToken()


@router.get('/', response_model=List[ContactsResponse], dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def get_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                       user: int = Depends(authtoken.get_current_user)):
    """
    The get_contacts function returns a list of contacts.

    :param skip: int: Skip the first n contacts in the database
    :param limit: int: Limit the number of contacts returned
    :param db: Session: Pass the database session to the function
    :param user: int: Get the current user
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await repository_contacts.get_contacts(skip, limit, user, db)
    return contacts


@router.post('/', response_model=ContactsResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def add_contact(body: ContactModel, db: Session = Depends(get_db),
                      user: int = Depends(authtoken.get_current_user)):
    """
    The add_contact function creates a new contact in the database.
    The function takes a ContactModel object as input, which is validated by Pydantic.
    The user_id of the current user is passed to the add_contact function from authtoken.py.

    :param body: ContactModel: Get the data from the request body
    :param db: Session: Pass the database session to the function
    :param user: int: Get the user id from the token
    :return: A contactmodel object
    :doc-author: Trelent
    """
    contact = await repository_contacts.add_contact(body, user, db)
    return contact


@router.get('/search', response_model=List[ContactsResponse], dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def search_contact(first_name: str = None, last_name: str = None, email: str = None,
                         db: Session = Depends(get_db), user: int = Depends(authtoken.get_current_user)):
    """
    The search_contact function searches for a contact in the database.
    It takes three parameters: first_name, last_name and email.
    If no parameter is given, it returns all contacts of the user.

    :param first_name: str: Search for a contact by first name
    :param last_name: str: Search the contact by last name
    :param email: str: Search for a contact by email
    :param db: Session: Get the database connection
    :param user: int: Get the user id from the authtoken
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await repository_contacts.search_contact(db, user, first_name, last_name, email)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contacts


@router.get('/birthdays', response_model=List[ContactsResponse], dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def get_birthdays(db: Session = Depends(get_db), user: int = Depends(authtoken.get_current_user)):
    """
    The get_birthdays function returns a list of contacts with birthdays in the next week.
    The user is determined by the authtoken passed to it.

    :param db: Session: Get the database session from the dependency
    :param user: int: Get the user id from the authtoken
    :return: A list of contacts with birthdays in the next week
    :doc-author: Trelent
    """
    contacts = await repository_contacts.get_birthdays(user, db)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No birthdays in next week")
    return contacts


@router.delete('/{contact_id}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def remove_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db),
                         user: int = Depends(authtoken.get_current_user)):
    """
    The remove_contact function removes a contact from the database.
    The function takes in an integer representing the id of the contact to be removed,
    and returns a dictionary containing information about that contact.

    :param contact_id: int: Get the contact id from the path
    :param db: Session: Get the database session
    :param user: int: Get the user id from the authtoken
    :return: The contact that was removed
    :doc-author: Trelent
    """
    contact = await repository_contacts.remove_contact(contact_id, user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.put('/{contact_id}', response_model=ContactsResponse, dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def change_contact(body: ContactModel, contact_id: int = Path(ge=1), db: Session = Depends(get_db),
                         user: int = Depends(authtoken.get_current_user)):
    """
    The change_contact function is used to change a contact in the database.
    The function takes in a ContactModel object, which contains all of the information for the new contact.
    It also takes an optional parameter of an integer representing the id of a specific contact to be changed.
    If no id is provided, then it will return an error message saying that there was no ID provided.

    :param body: ContactModel: Pass the data from the request body to the function
    :param contact_id: int: Specify the contact id of the contact to be deleted
    :param db: Session: Get the database session
    :param user: int: Get the user id from the token
    :return: A contactmodel
    :doc-author: Trelent
    """
    contact = await repository_contacts.get_contact(contact_id, user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    contact = await repository_contacts.change_contact(contact_id, body, user, db)
    return contact


@router.get('/{contact_id}', response_model=ContactsResponse, dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def get_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db),
                      user: int = Depends(authtoken.get_current_user)):
    """
    The get_contact function returns a contact by its id.
    If the contact does not exist, it raises an HTTP 404 error.

    :param contact_id: int: Specify the id of the contact to be retrieved
    :param db: Session: Get the database session
    :param user: int: Get the current user
    :return: A contact
    :doc-author: Trelent
    """
    contact = await repository_contacts.get_contact(contact_id, user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact
