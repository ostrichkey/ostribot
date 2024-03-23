# Instructions

1. Add nsec to file:
```
echo "nsec1abcdefgj...." > secrets/nsec.txt
```

2. create python venv

```
cd python
python3 -m venv env
```

3. source venv
```
source env/bin/activate
```

## run obot

```
cd python/obot
python3 obot.py
```



## Test encrypt_text function:
Test encryption of a plain text message to verify the correctness of encryption.

## Test BotEventHandler class:

Test adding a contact to the contact list.
Test receiving and processing contact list events.
Test replying to events with an encrypted message.
Test generating reply tags.
Test generating contact list tags.


## Test query_contact_list function:
Test querying the contact list from the server.

## Test main function:
Test the initialization of keys from a file.
Test the initialization of the client pool.
Test the subscription to event handlers.
Test the starting of clients.



# Test BotEventHandler class
# Add test functions for different methods of BotEventHandler

# Test query_contact_list function
# Add test function for query_contact_list

# Test main function
# Add test function for main