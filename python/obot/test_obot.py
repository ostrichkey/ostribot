import asyncio
import pytest
from unittest.mock import MagicMock, patch, AsyncMock, Mock
from obot import encrypt_text, BotEventHandler, query_contact_list, main, get_args
#from obot import encrypt_text, BotEventHandler, get_args, query_contact_list, main
from obot import *





#*************************Test encrypt_text function******************************#

@pytest.mark.parametrize("plain_text, to_pub_k, expected_result", [
    ("Test message", "public_key", "ZW5jcnlwdGVkX3RleHQ=?iv=aXZfZGF0YQ=="),
    # Add more test cases as needed
])
def test_encrypt_text(plain_text, to_pub_k, expected_result):
    encryptor_mock = MagicMock()
    encryptor_mock.encrypt_message.return_value = {'text': b'encrypted_text', 'iv': b'iv_data'}
    assert encrypt_text(encryptor_mock, plain_text, to_pub_k) == expected_result





#*************************Test BotEventHandler class******************************#
    
@pytest.fixture
def mock_event_handler_dependencies():
    # Mock dependencies for BotEventHandler
    as_user = Mock()
    as_user.private_key_hex.return_value = "abcdef0123456789" 
    clients = Mock()
    contact_list = ['contact1', 'contact2']
    message = "Test message"
    return as_user, clients, contact_list, message

def test_BotEventHandler_do_event_accepts_self(mock_event_handler_dependencies):
    # Arrange
    as_user, clients, contact_list, message = mock_event_handler_dependencies
    event_handler = BotEventHandler(as_user, clients, contact_list, message)
    mock_client = MagicMock()
    sub_id = 'test_sub_id'
    mock_event = Mock()
    mock_event.pub_key = as_user.public_key_hex()
    mock_event.kind = 1  # Example event kind

    # Act
    event_handler.do_event(mock_client, sub_id, mock_event)

    # Assert
    assert not mock_client.subscribe.called  # Ensure subscribe is not called

def test_BotEventHandler_add_contact_adds_to_contact_list(mock_event_handler_dependencies):
    # Arrange
    as_user, clients, contact_list, message = mock_event_handler_dependencies
    event_handler = BotEventHandler(as_user, clients, contact_list, message)
    pub_key = 'new_public_key'

    # Act
    result = event_handler._add_contact(pub_key)

    # Assert
    assert result is True
    assert pub_key in event_handler._contact_list

def test_BotEventHandler_add_contact_does_not_add_existing_contact(mock_event_handler_dependencies):
    # Arrange
    as_user, clients, contact_list, message = mock_event_handler_dependencies
    existing_pub_key = contact_list[0]
    event_handler = BotEventHandler(as_user, clients, contact_list, message)

    # Act
    result = event_handler._add_contact(existing_pub_key)

    # Assert
    assert result is False
    assert len(event_handler._contact_list) == len(contact_list)


#****************************Test query_contact_list function***********************#
# @pytest.fixture
# def mock_client_pool():
#     # Mock ClientPool object
#     mock_pool = MagicMock()
#     return mock_pool 

# @pytest.mark.asyncio
# def test_query_contact_list(mock_client_pool):
#     # Arrange
#     public_key = "test_public_key"
#     relays = ["relay1", "relay2"]
#     expected_events = ["event1", "event2"]  # Mock list of events returned by the client pool

#     # Mock the behavior of the client pool
#     mock_client_pool_instance = mock_client_pool.return_value
#     mock_client_pool_instance.query = AsyncMock(return_value=expected_events)

#     # Act
#     result = query_contact_list(public_key, relays)

#     # Assert
#     mock_client_pool.assert_called_once_with(relays)
#     mock_client_pool_instance.query.assert_awaited_once_with({
#         'kinds': ['contact_list'],
#         'authors': [public_key]
#     })
#     assert result == expected_events



#***************************************************#
# @pytest.fixture
# def mock_client_pool():
#     # Create a MagicMock object to mock the ClientPool
#     mock_pool = MagicMock()
#     return mock_pool    

# @pytest.mark.asyncio
# def test_query_contact_list(mock_client_pool):
#     # Define a mock event representing the contact list
#     mock_contact_list_event = {'tags': [['p', 'public_key_1'], ['p', 'public_key_2']], 'other_fields': 'other_values'}
    
#     # Mock the query method of ClientPool to return the mock event
#     mock_client_pool.query.return_value = [mock_contact_list_event]
    
#     # Call the query_contact_list function with the mock client pool
#     contact_list = query_contact_list(public_key='your_public_key', relays=['relay1', 'relay2'])
    
#     # Define the expected contact list based on the mock event
#     expected_contact_list = ['public_key_1', 'public_key_2']
    
#     # Assert that the returned contact list matches the expected contact list
#     assert contact_list == expected_contact_list




@pytest.fixture
def mock_client_pool():
    # Create a MagicMock object to mock the ClientPool
    mock_pool = MagicMock()
    return mock_pool    

# @pytest.mark.asyncio
# async def test_query_contact_list(mock_client_pool):
#     # Define a mock event representing the contact list
#     mock_contact_list_event = {'tags': [['p', 'public_key_1'], ['p', 'public_key_2']], 'other_fields': 'other_values'}
    
#     # Mock the query method of ClientPool to return the mock event
#     mock_client_pool.query.return_value = [mock_contact_list_event]
    
#     # Call the query_contact_list function with the mock client pool
#     contact_list_coroutine = query_contact_list(public_key='your_public_key', relays=['relay1', 'relay2'])
    
#     # Use asyncio's `await` to get the result of the coroutine
#     contact_list = await contact_list_coroutine
    
#     # Define the expected contact list based on the mock event
#     expected_contact_list = ['public_key_1', 'public_key_2']
    
#     # Assert that the returned contact list matches the expected contact list
#     assert contact_list == expected_contact_list



#****************************Test main function***********************#
@pytest.fixture
def mock_get_args():
    # Mock get_args function
    with patch('obot.get_args') as mock_get_args:
        mock_get_args.return_value = {'key': 'test_key_file', 'relays': ['relay1', 'relay2']}
        yield mock_get_args

@pytest.fixture
def mock_client_pool():
    # Mock ClientPool object
    with patch('obot.ClientPool') as mock_client_pool:
        yield mock_client_pool

@pytest.fixture
def mock_query_contact_list():
    # Mock query_contact_list function
    with patch('obot.query_contact_list') as mock_query_contact_list:
        yield mock_query_contact_list

@pytest.fixture
def mock_async_run():
    # Mock asyncio.run function
    with patch('obot.asyncio.run') as mock_async_run:
        yield mock_async_run

# def test_main_initialization(mock_get_args, mock_client_pool, mock_query_contact_list, mock_async_run):
#     # Arrange
#     # Create a mock user object
#     mock_user = Mock()
    
#     # Define the arguments to be returned by mock_get_args
#     args_to_return = {'key': 'test_key_file', 'relays': ['relay1', 'relay2']}
    
#     # Set up the expected arguments for ClientPool initialization
#     expected_client_pool_args = {'clients': ['relay1', 'relay2']}
    
#     # Get the mock client pool object
#     mock_clients = mock_client_pool.return_value
    
#     # Act
#     # Call the main function with the mock arguments
#     main(mock_get_args())
    
#     # Assert
#     # Check that mock_get_args is called once
#     mock_get_args.assert_called_once()
    
#     # Check that mock_client_pool is called once with the expected arguments
#     # Ensure the dictionary keys match exactly
#     mock_clients.assert_called_once_with(clients=['relay1', 'relay2'])  # Ensure key names match exactly

#     # Check that mock_query_contact_list is called once with the expected arguments
#     expected_query_args = {'public_key': mock_user.public_key_hex(), 'relays': args_to_return['relays']}
#     mock_query_contact_list.assert_called_once_with(**expected_query_args)
    
#     # Check that mock_async_run is called once
#     mock_async_run.assert_called_once()



def test_main_subscription(mock_get_args, mock_client_pool, mock_query_contact_list, mock_async_run):
    # Arrange
    mock_as_user = Mock()
    mock_clients = mock_client_pool.return_value

    # Act
    main(mock_get_args())

    # Assert
    assert mock_clients.set_on_connect.called_once()
    assert mock_clients.run.called_once()