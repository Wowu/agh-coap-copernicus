#!/usr/bin/env python3
import argparse
import asyncio
import signal
import sys

import aiocoap.resource as resource
from aiocoap import Context

from VirtualCopernicusNG import TkCircuit
from resources import ServoResource, LEDResource, ButtonResource, BuzzerResource, GPIOResource
from virtual_config import configuration

SERVER_IP = '0.0.0.0'


def virtual():
    """Simulate coap resources in VirtualCopernicus"""
    circuit = TkCircuit(configuration)

    root = resource.Site()
    root.add_resource(['.well-known', 'core'], resource.WKCResource(root.get_resources_as_linkheader))
    root.add_resource(['servo'], ServoResource(17))
    root.add_resource(['led1'], LEDResource(21))
    root.add_resource(['led2'], LEDResource(22))
    root.add_resource(['button1'], ButtonResource(11, lambda: print("Button1 pressed")))
    root.add_resource(['button2'], ButtonResource(12))
    root.add_resource(['buzzer'], BuzzerResource(16))
    root.add_resource(['gpio_buzzer'], GPIOResource(15))

    @circuit.run
    def main():
        asyncio.set_event_loop(event_loop)
        asyncio.Task(Context.create_server_context(root, bind=(SERVER_IP, 5683)))
        event_loop.run_forever()


def physical():
    """Run coap resources on real raspberry pi"""
    root = resource.Site()
    root.add_resource(['.well-known', 'core'], resource.WKCResource(root.get_resources_as_linkheader))
    root.add_resource(['led'], LEDResource(17))
    root.add_resource(['buzzer'], BuzzerResource(22, active_high=False))
    root.add_resource(['button'], ButtonResource(27, lambda: print("Button pressed")))

    asyncio.set_event_loop(event_loop)
    asyncio.Task(Context.create_server_context(root, bind=(SERVER_IP, 5683)))
    event_loop.run_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run CoAP server')
    parser.add_argument('device', metavar='device_type', type=str,
                        help='selects device type', choices=['gpiozero', 'virtual'])
    parser.add_argument('address', nargs='?', metavar='server_address', type=str,
                        help='CoAP server address', default="0.0.0.0")

    args = parser.parse_args()
    SERVER_IP = args.address
    event_loop = asyncio.get_event_loop()

    # use virtual or gpiozero devices
    if args.device == 'gpiozero':
        physical()
    elif args.device == 'virtual':
        signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))  # "proper" closing of tkinter
        virtual()
