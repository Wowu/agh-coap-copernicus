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
        code=Code.GET,
        uri=f'coap://127.0.0.1/{name}'
    )

    try:
        response = await context.request(request).response
        format_response(response.code, response.payload)
    except Exception as e:
        print(f'Failed to fetch resource: {name}')
        print(e)


async def set_value(name: str, val: str):
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
        user_input = input('')
        if user_input == 'e':
            print("Goodbye!")
            break

        tokens = user_input.split(' ')
        cmd = tokens[0]
        try:
            params = tokens[1:]
        except:
            params = []

        if cmd == 'g':
            await get_value(params[0])
        elif cmd == 's':
            await set_value(params[0], " ".join(params[1:]))


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
