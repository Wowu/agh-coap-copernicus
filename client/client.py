#!/usr/bin/env python3

import argparse
import asyncio

from aiocoap import Context, Message, Code

SERVER_IP = "127.0.0.1"

def format_response(code, payload):
    print(f"Response: {code}")
    if len(payload) > 0:
        print(payload.decode('utf-8'))


async def get_value(name: str):
    context = await Context.create_client_context()

    request = Message(
        code=Code.GET,
        uri=f'coap://{SERVER_IP}/{name}'
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
        uri=f'coap://{SERVER_IP}/{name}',
        payload=str(val).encode()
    )

    try:
        response = await context.request(request).response
        format_response(response.code, response.payload)
    except Exception as e:
        print('Failed to set resource:')
        print(e)


async def main():
    global SERVER_IP

    parser = argparse.ArgumentParser(description='Run CoAP Client')
    parser.add_argument('address', nargs='?', metavar='server_address', type=str,
                        help='CoAP server address', default="127.0.0.1" )

    args = parser.parse_args()
    SERVER_IP = args.address

    print(f"CoAP Client - Connected to: {SERVER_IP}")
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
            if cmd == 'g':
                await get_value(params[0])
            elif cmd == 's':
                await set_value(params[0], " ".join(params[1:]))
        except:
            print("Bad command")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
