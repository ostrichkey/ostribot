import asyncio
import pytest
from unittest.mock import MagicMock, patch, AsyncMock, Mock
from obot import *
import unittest
from obot import BotEventHandler, encrypt_text, query_contact_list, main

#****************************************Test encrypt_text function***********************************#

@pytest.mark.parametrize("plain_text, to_pub_k, expected_result", [
    ("Test message", "public_key", "ZW5jcnlwdGVkX3RleHQ=?iv=aXZfZGF0YQ=="),   
])
def test_encrypt_text(plain_text, to_pub_k, expected_result):
    encryptor_mock = MagicMock()
    encryptor_mock.encrypt_message.return_value = {'text': b'encrypted_text', 'iv': b'iv_data'}
    assert encrypt_text(encryptor_mock, plain_text, to_pub_k) == expected_result

#**********************************Test BotEventHandler class****************************************#
    
@pytest.fixture
def mock_event_handler_dependencies():
    as_user = Mock()
    as_user.private_key_hex.return_value = "abcdef0123456789" 
    clients = Mock()
    contact_list = ['contact1', 'contact2']
    message = "Test message"
    return as_user, clients, contact_list, message

def test_BotEventHandler_do_event_accepts_self(mock_event_handler_dependencies):
    as_user, clients, contact_list, message = mock_event_handler_dependencies
    event_handler = BotEventHandler(as_user, clients, contact_list, message)
    mock_client = MagicMock()
    sub_id = 'test_sub_id'
    mock_event = Mock()
    mock_event.pub_key = as_user.public_key_hex()
    mock_event.kind = 1

    event_handler.do_event(mock_client, sub_id, mock_event)
    assert not mock_client.subscribe.called

def test_BotEventHandler_add_contact_adds_to_contact_list(mock_event_handler_dependencies):
    as_user, clients, contact_list, message = mock_event_handler_dependencies
    event_handler = BotEventHandler(as_user, clients, contact_list, message)
    pub_key = 'new_public_key'
    result = event_handler._add_contact(pub_key)
    assert result is True
    assert pub_key in event_handler._contact_list

def test_BotEventHandler_add_contact_does_not_add_existing_contact(mock_event_handler_dependencies):
    as_user, clients, contact_list, message = mock_event_handler_dependencies
    existing_pub_key = contact_list[0]
    event_handler = BotEventHandler(as_user, clients, contact_list, message)
    result = event_handler._add_contact(existing_pub_key)
    assert result is False
    assert len(event_handler._contact_list) == len(contact_list)



#******************************Test query_contact_list function*************************************#
    
class TestQueryContactList(unittest.TestCase):
    @patch('obot.ClientPool')
    async def test_query_contact_list(self, mock_client_pool):
        public_key = "sample_public_key"
        relays = ["Relay1", "Relay2"]
        expected_contact_list = ["Contact1", "Contact2"]
        mock_client_pool.return_value.__aenter__.return_value.query.return_value = [MagicMock(tags=[('p', contact) for contact in expected_contact_list])]
        contact_list = await query_contact_list(public_key, relays)
        self.assertEqual(contact_list, expected_contact_list)



#*********************************Test main function***************************#
        
@pytest.fixture
def mock_get_args():
    with patch('obot.get_args') as mock_get_args:
        mock_get_args.return_value = {'key': 'test_key_file', 'relays': ['relay1', 'relay2']}
        yield mock_get_args


@pytest.fixture
def mock_client_pool():
    # Define mock_clients here
    with patch('obot.ClientPool') as mock_client_pool:
        mock_clients = mock_client_pool.return_value
        yield mock_clients



@pytest.fixture
def mock_query_contact_list():
    with patch('obot.query_contact_list') as mock_query_contact_list:
        yield mock_query_contact_list

@pytest.fixture
def mock_async_run():
    with patch('obot.asyncio.run') as mock_async_run:
        yield mock_async_run

def test_main_subscription(mock_get_args, mock_client_pool, mock_query_contact_list, mock_async_run):
    main(mock_get_args())
    # Use mock_clients defined in mock_client_pool fixture
    assert mock_client_pool.set_on_connect.called_once()
    assert mock_client_pool.run.called_once()

class TestMainFunction(unittest.TestCase):
    def setUp(self):
        self.args = {'message': 'Sample message', 'key': 'sample_key', 'relays': ['Relay1', 'Relay2']}

    @patch('builtins.print')
    @patch('obot.ClientPool')
    async def test_main(self, mock_client_pool, mock_print):
        mock_client_pool.return_value.run.side_effect = asyncio.CancelledError
        with self.assertRaises(asyncio.CancelledError):
            await main(self.args)

    @patch('obot.query_contact_list')
    @patch('obot.ClientPool')
    @patch('builtins.print')
    async def test_main_with_contact_list(self, mock_print, mock_client_pool, mock_query_contact_list):
        mock_query_contact_list.return_value = ['Contact1', 'Contact2']
        mock_client_pool.return_value.run.side_effect = asyncio.CancelledError
        with self.assertRaises(asyncio.CancelledError):
            await main(self.args)










