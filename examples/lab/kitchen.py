#!/usr/bin/env python3
import argparse
import asyncio
import signal
import sys

import aiocoap.resource as resource
from aiocoap import Code, Context, Message
from resources import LEDResource, ButtonResource, BuzzerResource

from VirtualCopernicusNG import TkCircuit
from virtual_config import configuration

SERVER_IP = '0.0.0.0'


async def observe_button(ip, name, callback):
    context = await Context.create_client_context()
    await asyncio.sleep(2)

    request = Message(
        code=Code.GET,
        uri=f'coap://{ip}/{name}',
        observe=0
    )

    requester = context.request(request)
    # requester.observation.register_callback(callback) # TODO: callback is better method
    # callback func requires one parameter

    async for message in requester.observation:
        if message.payload == b'1':  # button pressed
            callback()


def configure_resources():
    def main_func():
        led1 = LEDResource(21)
        led2 = LEDResource(22)

        root = resource.Site()
        root.add_resource(['.well-known', 'core'], resource.WKCResource(root.get_resources_as_linkheader))
        root.add_resource(['led1'], led1)
        root.add_resource(['led2'], led2)
        root.add_resource(['button1'], ButtonResource(11, lambda: led1.resource.toggle(), loop=event_loop))
        root.add_resource(['button2'], ButtonResource(12, loop=event_loop))

        tasks = []

        asyncio.set_event_loop(event_loop)
        asyncio.Task(Context.create_server_context(root, bind=(SERVER_IP, 5683)))
        tasks.append(asyncio.ensure_future(observe_button('127.0.0.3', 'shutter', lambda: led1.resource.off())))
        tasks.append(asyncio.ensure_future(observe_button('127.0.0.5', 'button2', lambda: led1.resource.toggle())))
        event_loop.run_forever()

        for t in tasks:
            t.cancel()

    return main_func


def physical(run_func):
    """Run coap resources on real raspberry pi"""
    run_func()


def virtual(run_func):
    """Simulate coap resources in VirtualCopernicus"""
    new_configuration = configuration
    new_configuration['name'] = 'Kitchen'
    circuit = TkCircuit(new_configuration)

    @circuit.run
    def main():
        run_func()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run CoAP server')
    parser.add_argument('device', metavar='device_type', type=str,
                        help='selects device type', choices=['gpiozero', 'virtual'])
    parser.add_argument('address', nargs='?', metavar='server_address', type=str,
                        help='CoAP server address', default="0.0.0.0")

    args = parser.parse_args()
    SERVER_IP = args.address
    event_loop = asyncio.get_event_loop()
    run_func = configure_resources()

    if args.device == 'gpiozero':
        physical(run_func)
    elif args.device == 'virtual':
        signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))  # "proper" closing of tkinter
        virtual(run_func)
