#!/usr/bin/env python3

import logging
import asyncio

from aiocoap import *

logging.basicConfig(level=logging.INFO)


async def get_angle():
    context = await Context.create_client_context()

    request = Message(
        code=GET,
        uri='coap://localhost/servo'
    )

    try:
        response = await context.request(request).response
        print('Result: %s\n%r' % (response.code, response.payload))
    except Exception as e:
        print('Failed to fetch resource:')
        print(e)


async def set_angle(val):
    context = await Context.create_client_context()

    request = Message(
        code=POST,
        uri='coap://localhost/servo',
        payload=str(val).encode()
    )

    try:
        await context.request(request).response
    except Exception as e:
        print('Failed to set resource:')
        print(e)


async def main():
    print("e - exit")
    print("g - get resource value")
    print("s v - set resource value to v")
    while True:
        user_input = input('> ')
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
            'g': get_angle,
            's': set_angle
        }[cmd]

        await command(*params)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
