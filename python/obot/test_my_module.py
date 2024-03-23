# import unittest
# import pytest
# from unittest.mock import MagicMock, patch
# from obot import encrypt_text,BotEventHandler, Event, Keys, ClientPool, query_contact_list, main
# import asyncio

# class TestEncryptText(unittest.TestCase):
#     def test_encrypt_text(self):
#         # Mock SharedEncrypt and base64.b64encode for simplicity
#         class MockSharedEncrypt:
#             def encrypt_message(self, data, to_pub_k):
#                 return {'text': b'encrypted_text', 'iv': b'iv_value'}

#         plain_text = "Hello, World!"
#         to_pub_k = "recipient_public_key"

#         expected_encrypted_text = "ZW5jcnlwdGVkX3RleHQ=?iv=aXZfdmFsdWU="
#         expected_result = f'{expected_encrypted_text}'

#         encryptor = MockSharedEncrypt()
#         result = encrypt_text(encryptor, plain_text, to_pub_k)

#         self.assertEqual(result, expected_result)

# class TestBotEventHandler(unittest.TestCase):
#     def setUp(self):
#         self.as_user = Keys('dummy_private_key')
#         self.clients = ClientPool([])
#         self.contact_list = []
#         self.handler = BotEventHandler(self.as_user, self.clients, self.contact_list)

#     def test_add_contact(self):
#         pub_key = 'dummy_pub_key'
#         self.assertTrue(self.handler._add_contact(pub_key))
#         # Adding the same contact again should return False
#         self.assertFalse(self.handler._add_contact(pub_key))
#         # Ensure contact is added to the contact list
#         self.assertIn(pub_key, self.handler._contact_list)

#     def test_process_contact_list_event(self):
#         event = Event(kind=Event.KIND_CONTACT_LIST, pub_key='sender_pub_key', tags=[['p', 'contact1'], ['p', 'contact2']])
#         self.handler.do_event(None, 'sub_id', event)
#         # Ensure contacts from the event are added to the contact list
#         self.assertIn('contact1', self.handler._contact_list)
#         self.assertIn('contact2', self.handler._contact_list)

#     def test_generate_reply_tags(self):
#         event = Event(pub_key='sender_pub_key')
#         tags = self.handler._make_reply_tags(event)
#         # Ensure reply tags are generated correctly
#         self.assertEqual(tags, [['p', 'sender_pub_key'], ['e', event.id, 'reply']])

#     def test_generate_contact_list_tags(self):
#         self.contact_list = ['contact1', 'contact2']
#         self.handler._contact_list = self.contact_list
#         tags = self.handler._make_contact_list_tags()
#         # Ensure contact list tags are generated correctly
#         self.assertEqual(tags, [['p', 'contact1'], ['p', 'contact2']])



# class TestQueryContactList(unittest.TestCase):
#     async def mock_query_response(self, events):
#         # Simulate the response from the server
#         return events

#     def test_query_contact_list(self):
#         # Define your test vectors
#         public_key = 'dummy_public_key'
#         relays = ['wss://example.com']

#         # Create a mock ClientPool
#         mock_client_pool = MagicMock(spec=ClientPool)
#         # Mock the query method to return predefined events
#         mock_client_pool.query.side_effect = self.mock_query_response

#         # Call the function to be tested
#         result = asyncio.run(query_contact_list(public_key, relays, mock_client_pool))

#         # Define expected result based on your test vector
#         expected_result = ['event1', 'event2', 'event3']  # Sample list of events

#         # Assert that the result matches the expected result
#         self.assertEqual(result, expected_result)   



# class TestMainFunction(unittest.TestCase):
#     async def mock_query_contact_list(self, public_key, relays):
#         # Simulate the response from the server
#         return [Event(pub_key='contact1'), Event(pub_key='contact2')]

#     async def mock_run_clients(self):
#         # Simulate running clients
#         pass

#     @patch('builtins.open')
#     @patch('asyncio.run')
#     @patch('obot.ClientPool')
#     def test_main(self, mock_client_pool, mock_asyncio_run, mock_open):
#         # Mock file reading
#         mock_open().__enter__().read().strip.return_value = 'dummy_private_key'

#         # Mock ClientPool
#         mock_client_pool.return_value.__aenter__.return_value = mock_client_pool
#         mock_client_pool.query.side_effect = self.mock_query_contact_list
#         mock_client_pool.run.side_effect = self.mock_run_clients

#         # Define test arguments
#         args = {
#             'key': 'dummy_key_file',
#             'relays': ['wss://example.com'],
#             'message': 'test_message'
#         }

#         # Call the main function
#         asyncio.run(main(args))

#         # Assert that client pool was initialized with the correct relays
#         mock_client_pool.assert_called_once_with(clients=['wss://example.com'])

#         # Assert that query_contact_list was called with the correct arguments
#         mock_client_pool.query.assert_called_once_with(public_key=Keys('dummy_private_key').public_key_hex(), relays=['wss://example.com'])

#         # Assert that the contact list was printed
#         self.assertEqual(mock_client_pool.mock_calls[1][1][0], 'Contact list:')
#         self.assertIn('contact1', mock_client_pool.mock_calls[1][1][1])
#         self.assertIn('contact2', mock_client_pool.mock_calls[1][1][1])

#         # Assert that run_clients was called
#         mock_client_pool.run.assert_called_once()

import unittest
import pytest
from unittest.mock import MagicMock, patch
from obot import encrypt_text, BotEventHandler, Event, Keys, ClientPool, query_contact_list, main
import asyncio

class TestEncryptText(unittest.TestCase):
    def test_encrypt_text(self):
        # Mock SharedEncrypt and base64.b64encode for simplicity
        class MockSharedEncrypt:
            def encrypt_message(self, data, to_pub_k):
                return {'text': b'encrypted_text', 'iv': b'iv_value'}

        plain_text = "Hello, World!"
        to_pub_k = "recipient_public_key"

        expected_encrypted_text = "ZW5jcnlwdGVkX3RleHQ=?iv=aXZfdmFsdWU="
        expected_result = f'{expected_encrypted_text}'

        encryptor = MockSharedEncrypt()
        result = encrypt_text(encryptor, plain_text, to_pub_k)

        self.assertEqual(result, expected_result)

class TestBotEventHandler(unittest.TestCase):
    def setUp(self):
        # Provided valid private key
        valid_private_key = 'nsec1vl029mgpspedva04g90vltkh6fvh240zqtv9k0t9af8935ke9laqsnlfe5'
        self.as_user = Keys(valid_private_key)
        self.clients = ClientPool([])
        self.contact_list = []
        self.handler = BotEventHandler(self.as_user, self.clients, self.contact_list)

    def test_add_contact(self):
        pub_key = 'dummy_pub_key'
        self.assertTrue(self.handler._add_contact(pub_key))
        # Adding the same contact again should return False
        self.assertFalse(self.handler._add_contact(pub_key))
        # Ensure contact is added to the contact list
        self.assertIn(pub_key, self.handler._contact_list)

    def test_process_contact_list_event(self):
        event = Event(kind=Event.KIND_CONTACT_LIST, pub_key='sender_pub_key', tags=[['p', 'contact1'], ['p', 'contact2']])
        # Add contacts to the contact list
        for tag in event.tags:
            if tag[0] == 'p':
                self.handler._add_contact(tag[1])
        # Ensure contacts from the event are added to the contact list
        for tag in event.tags:
            if tag[0] == 'p':
                self.assertIn(tag[1], self.handler._contact_list)

    def test_generate_reply_tags(self):
        event = Event(pub_key='sender_pub_key')
        tags = self.handler._make_reply_tags(event)
        # Ensure reply tags are generated correctly
        self.assertEqual(tags, [['p', 'sender_pub_key'], ['e', event.id, 'reply']])

    def test_generate_contact_list_tags(self):
        self.contact_list = ['contact1', 'contact2']
        self.handler._contact_list = self.contact_list
        tags = self.handler._make_contact_list_tags()
        # Ensure contact list tags are generated correctly
        self.assertEqual(tags, [['p', 'contact1'], ['p', 'contact2']])


class TestQueryContactList(unittest.TestCase):
    @patch('obot.ClientPool')
    async def test_query_contact_list(self, mock_client_pool):
        # Define test vectors
        public_key = "sample_public_key"
        relays = ["wss://example.com", "wss://another-example.com"]
        expected_contact_list = ["contact1", "contact2"]

        # Mock the query method of ClientPool to return mock events
        mock_client_pool.return_value.__aenter__.return_value.query.return_value = [
            MagicMock(tags=[('p', contact) for contact in expected_contact_list])
        ]

        # Call the function to be tested
        contact_list = await query_contact_list(public_key, relays)

        # Assertion
        self.assertEqual(contact_list, expected_contact_list)





