#!/usr/bin/env python3

import logging
import asyncio

import aiocoap
from aiocoap import Context, Message, Code

logging.basicConfig(level=logging.INFO)


def format_response(code, payload):
    print(f"Response: {code}")
    print(payload.decode('utf-8'))


async def get_value(name: str):
    context = await Context.create_client_context()

    request = Message(
        code=aiocoap.GET,
        uri=f'coap://127.0.0.1/{name}'
    )

    try:
        response = await context.request(request).response
        format_response(response.code, response.payload)
    except Exception as e:
        print(f'Failed to fetch resource: {name}')
        print(e)


async def set_angle(name: str, val):
    context = await Context.create_client_context()

    request = Message(
        code=Code.POST,
        uri=f'coap://127.0.0.1/{name}',
        payload=str(val).encode()
    )

    try:
        response = await context.request(request).response
        format_response(response.code, response.payload)
    except Exception as e:
        print('Failed to set resource:')
        print(e)


async def main():
    print("e - exit")
    print("g name - get resource value")
    print("s name v - set resource value to v")
    while True:
        # user_input = input('> ')
        user_input = input('')
        if user_input == 'e':
            print("bye")
            break

        tokens = user_input.split(' ')
        cmd = tokens[0]
        try:
            params = tokens[1:]
        except:
            params = []

        command = {
            'g': get_value,
            's': set_angle
        }[cmd]

        try:
            await command(*params)
        except:
            pass


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
