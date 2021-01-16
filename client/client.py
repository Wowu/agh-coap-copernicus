#!/usr/bin/env python3

import argparse
import asyncio
from aioconsole import ainput

from aiocoap import Context, Message, Code


async def main(client):
    await client.create_client_context()

    print(f"CoAP Client - Connected to: {client.ip}")
    print("e - exit")
    print("g name - get resource value")
    print("s name v - set resource value to v")
    print("o name - observe resource")
    while True:
        user_input = await ainput('>> ')
        if user_input == 'e':
            print("Goodbye!")
            break

        tokens = user_input.split(' ')
        cmd = tokens[0]
        try:
            params = tokens[1:]
            if cmd == 'g':
                await client.get_value(params[0])
            elif cmd == 's':
                await client.set_value(params[0], " ".join(params[1:]))
            elif cmd == 'o':
                asyncio.ensure_future(client.observe_resource(params[0]))

        except Exception as e:
            print(e)

    # seems like aiocoap does not fully support cancelling
    # https://github.com/chrysn/aiocoap/issues/187
    client.observed_resources.stop_observing()


class ObservedResourcesEntry:
    def __init__(self, requester, cancel):
        self.requester = requester
        self.cancel = cancel


class ObservedResources:
    def __init__(self):
        self.resources = {}

    def add(self, name, req, cancel):
        self.resources[name] = ObservedResourcesEntry(req, cancel)

    def stop_observing(self):
        for cancel_func in map(lambda x: x.cancel, self.resources.values()):
            cancel_func()


class Client:
    def __init__(self, ip):
        self.ip = ip
        self.observed_resources = ObservedResources()
        self.context = None
        self.default_callback = lambda m: print(f'[{m.code}]: {m.payload.decode("utf-8")}')
        self.default_error_callback = lambda m: print(f'ERROR: {m}')

    async def create_client_context(self):
        self.context = await Context.create_client_context()

    async def get_value(self, name: str):
        request = Message(
            code=Code.GET,
            uri=f'coap://{self.ip}/{name}'
        )

        await self.send_request(request)

    async def set_value(self, name: str, val: str):
        request = Message(
            code=Code.POST,
            uri=f'coap://{self.ip}/{name}',
            payload=str(val).encode()
        )

        await self.send_request(request)

    async def send_request(self, request):
        try:
            response = await self.context.request(request).response
            self.print_response(response.code, response.payload)
        except Exception as e:
            print('Failed to set resource:')
            print(e)

    async def observe_resource(self, name, cb=None, err_cb=None):
        observation_is_over = asyncio.Future()

        request = Message(
            code=Code.GET,
            uri=f'coap://{self.ip}/{name}',
            observe=0
        )

        requester = self.context.request(request)
        requester.observation.register_callback(self.default_callback if cb is None else cb)
        requester.observation.register_errback(self.default_error_callback if err_cb is None else err_cb)

        self.observed_resources.add(name, requester, requester.observation.cancel)

        await observation_is_over
        return requester

    def print_response(self, code, payload):
        print(f"Response: {code}")
        if len(payload) > 0:
            print(payload.decode('utf-8'))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run CoAP Client')
    parser.add_argument('address', nargs='?', metavar='server_address', type=str,
                        help='CoAP server address', default="127.0.0.1")

    args = parser.parse_args()
    asyncio.get_event_loop().run_until_complete(main(Client(args.address)))
