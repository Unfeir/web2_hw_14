from unittest.mock import MagicMock, patch, AsyncMock

import pytest

from src.database.models import User, Contact
from src.services.auth import AuthToken, AuthPassword

authtoken = AuthToken()
authpassword = AuthPassword()


def test_add_contact(client, session, token, user, contact, monkeypatch):
    with patch.object(authtoken, 'r') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())
        current_user = session.query(User).filter_by(email=user.get('email')).first()
        contact['user_id'] = current_user.id
        response = client.post(
            "/api/contacts/",
            json=contact,
            headers={'Authorization': f'Bearer {token["access_token"]}'}
        )
        assert response.status_code == 201, response.text
        my_contact = response.json()
        assert my_contact['email'] == contact['email']
        assert 'user_id' in my_contact
        # print(my_contact)


def test_get_contacts(client, session, token, contact, monkeypatch):
    with patch.object(authtoken, 'r') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        response = client.get(
            "/api/contacts/",
            headers={'Authorization': f'Bearer {token["access_token"]}'}
        )
        data = response.json()
        assert response.status_code == 200, response.text
        assert type(data) == list
        assert data[0]['email'] == contact['email']


def test_search_contact(client, session, token, contact, monkeypatch):
    with patch.object(authtoken, 'r') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        response = client.get(
            "/api/contacts/search/",
            params={'email': "poll@example.com"},
            headers={'Authorization': f'Bearer {token["access_token"]}'}
        )
        data = response.json()
        assert response.status_code == 200, response.text
        assert data[0]['email'] == contact['email']


def test_put_contact(client, session, token, user, contact, monkeypatch):
    with patch.object(authtoken, 'r') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        test_contact = session.query(Contact).filter_by(email=contact.get("email")).first()
        body = contact.copy()
        body['email'] = 'newemail@email.com'
        response = client.put(
            f"/api/contacts/{test_contact.id}/",
            json=body,
            headers={'Authorization': f'Bearer {token["access_token"]}'}
        )
        updated_contact = response.json()
        assert updated_contact['email'] == body['email']


def test_delete_contact(client, session, token, user, contact, monkeypatch):
    with patch.object(authtoken, 'r') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        test_contact = session.query(Contact).filter_by(first_name=contact.get("first_name")).first()
        client.delete(
            f"/api/contacts/{test_contact.id}/",
            headers={'Authorization': f'Bearer {token["access_token"]}'}
        )
        try_find = session.query(Contact).filter_by(first_name=contact.get("first_name")).first()
        assert try_find == None


