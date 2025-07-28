import pytest
from app import app
from unittest.mock import patch, MagicMock


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret'
    with app.test_client() as client:
        yield client


@patch('app.mysql')
def test_login_success(mock_mysql, client):
    # Arrange
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {
        'id': 1, 'username': 'testuser', 'password': 'testpass'
    }
    mock_mysql.connection.cursor.return_value = mock_cursor

    # Act
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    }, follow_redirects=True)

    # Assert
    assert response.status_code == 200
    assert b'Logged in successfully' in response.data


@patch('app.mysql')
def test_login_failure(mock_mysql, client):
    # Arrange
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_mysql.connection.cursor.return_value = mock_cursor

    # Act
    response = client.post('/login', data={
        'username': 'invalid',
        'password': 'wrong'
    }, follow_redirects=True)

    # Assert
    assert response.status_code == 200
    assert b'Incorrect username / password' in response.data


@patch('app.mysql')
def test_register_success(mock_mysql, client):
    # Arrange
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_mysql.connection.cursor.return_value = mock_cursor

    # Act
    response = client.post('/register', data={
        'username': 'newuser',
        'password': 'newpass',
        'email': 'new@example.com',
        'organisation': 'Org',
        'address': '123 Lane',
        'city': 'City',
        'state': 'State',
        'country': 'Country',
        'postalcode': '12345'
    }, follow_redirects=True)

    # Assert
    assert response.status_code == 200
    assert b'You have successfully registered' in response.data


@patch('app.mysql')
def test_update_account(mock_mysql, client):
    with client.session_transaction() as sess:
        sess['loggedin'] = True
        sess['id'] = 1

    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None  # no conflict
    mock_mysql.connection.cursor.return_value = mock_cursor

    response = client.post('/update', data={
        'username': 'updateduser',
        'password': 'updatedpass',
        'email': 'updated@example.com',
        'organisation': 'NewOrg',
        'address': 'New Address',
        'city': 'New City',
        'state': 'New State',
        'country': 'New Country',
        'postalcode': '54321'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'You have successfully updated' in response.data
