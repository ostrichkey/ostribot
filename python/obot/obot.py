import logging
import asyncio
from datetime import datetime
from monstr.client.client import Client, ClientPool
from monstr.client.event_handlers import EventHandler,DeduplicateAcceptor
from monstr.event.event import Event
from monstr.encrypt import SharedEncrypt, Keys
from monstr.util import util_funcs
from monstr.signing import BasicKeySigner

import base64
import argparse

 
def encrypt_text(encryptor: SharedEncrypt, plain_text: str, to_pub_k: str) -> str:
    crypt_message = encryptor.encrypt_message(data=bytes(plain_text.encode('utf8')),
                                              to_pub_k=to_pub_k)
    enc_message = base64.b64encode(crypt_message['text'])
    iv_env = base64.b64encode(crypt_message['iv'])
    return f'{enc_message.decode()}?iv={iv_env.decode()}'

class BotEventHandler(EventHandler):

    def __init__(self, as_user: Keys, clients: ClientPool, contact_list: list, message=""):
        self._as_user = as_user
        self._clients = clients
        self._contact_list = contact_list
        self._encryptor = SharedEncrypt(as_user.private_key_hex())
        self._message = message

        # track count times we replied to each p_pub_k
        self._replied = {}
        super().__init__(event_acceptors=[DeduplicateAcceptor()])

    def _make_reply_tags(self, src_evt: Event) -> list:
        """
            minimal tagging just that we're replying to sec_evt and tag in the creater pk so they see our reply
        """
        return [
            ['p', src_evt.pub_key],
            ['e', src_evt.id, 'reply']
        ]

    def _make_contact_list_tags(self) -> list:
        """
            creating contact list tags 
        """
        return [['p', p] for p in self._contact_list]

    def _add_contact(self, pub_key: str) -> bool:
        """
        Add contact to contact list.

        returns False if contact already in list.
        """
        follower = pub_key
        if follower not in self._contact_list:
            self._contact_list.append(follower)
            return True
        else:
            return False

    def do_event(self, the_client: Client, sub_id, evt: Event):
        # replying to ourself would be bad! also call accept_event
        # to stop us replying mutiple times if we see the same event from different relays
        if evt.pub_key == self._as_user.public_key_hex() or \
                self.accept_event(the_client, sub_id, evt) is False:
            return

        logging.debug('BotEventHandler::do_event - received event %s' % evt)

        if evt.kind in [Event.KIND_CONTACT_LIST]:
            if self._add_contact(evt.pub_key): # if contact is new
                logging.debug('BotEventHandler::do_event - contact_list = %s' % evt.pub_key)
                follow_event = Event(
                    kind=3,
                    content="",
                    tags=self._make_contact_list_tags(),
                    pub_key=self._as_user.public_key_hex()
                )
                follow_event.sign(self._as_user.private_key_hex())
                self._clients.publish(follow_event)

                if self._message: # if message is not empty  
                    response_event = Event(
                        kind=4,
                        content=encrypt_text(self._encryptor, self._message, evt.pub_key),
                        tags=self._make_reply_tags(evt),
                        pub_key=self._as_user.public_key_hex()
                    )

                    response_event.sign(self._as_user.private_key_hex())
                    self._clients.publish(response_event)

    def get_response_text(self, the_event):
        # possible parse this text also before passing onm
        prompt_text = the_event.content
        if the_event.kind == Event.KIND_ENCRYPT:
            prompt_text = the_event.decrypted_content(priv_key=self._as_user.private_key_hex(),
                                                      pub_key=the_event.pub_key)

        # do whatever to get the response
        pk = the_event.pub_key
        reply_n = self._replied[pk] = self._replied.get(pk, 0)+1
        reply_name = util_funcs.str_tails(pk)

        response_text = f'hey {reply_name} this is reply {reply_n} to you'

        return prompt_text, response_text

async def query_contact_list(public_key, relays):
    """
    query contact list
    """
    async with ClientPool(relays) as c:
        events = await c.query({
            'kinds': [Event.KIND_CONTACT_LIST],
            'authors': [public_key]
        })

        return events

async def main(args):
    # just the keys , change to profile?
    key_file = args['key']
    


    with open(key_file,'r') as f:
        as_user = Keys(f.read().strip())

    # relays we'll watch
    relays = args['relays']

    # the actually clientpool obj
    my_clients = ClientPool(clients=relays)

    contact_lists = await query_contact_list(public_key=as_user.public_key_hex(), relays=relays)
    contact_list = []
    if contact_lists:
        evt = contact_lists[0]
        contact_list = [t[1] for t in evt.tags if t[0] == 'p']
    
    print("Contact list:")
    print(contact_list)

    # do_event of this class is called on recieving events that match teh filter we reg for
    my_handler = BotEventHandler(as_user=as_user,
                                 clients=my_clients,
                                 contact_list=contact_list,
                                 message = args['message'])

    # called on first connect and any reconnects, registers our event listener
    def on_connect(the_client: Client):
        the_client.subscribe(sub_id='bot_watch',
                             handlers=[my_handler],
                             filters={
                                 'kinds': [Event.KIND_ENCRYPT,
                                           Event.KIND_CONTACT_LIST],
                                 '#p': [as_user.public_key_hex()],
                                 'since': util_funcs.date_as_ticks(datetime.now())
                             })
    # add the on_connect
    my_clients.set_on_connect(on_connect)

    # start the clients
    print('monitoring for events from or to account %s on relays %s' % (as_user.public_key_hex(),
                                                                        relays))
    await my_clients.run()


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--message', default="thx for the follow :) do you want to join the free raffle?")
    parser.add_argument('--key', default="../../secrets/nsec.txt")
    parser.add_argument('--relays', type=list, nargs="+", default=["wss://nos.lol","wss://relay.damus.io"])
    
    return vars(parser.parse_args())

if __name__ == "__main__":    


    logging.getLogger().setLevel(logging.DEBUG)
    asyncio.run(main(get_args()))

