#!/usr/bin/env python3

from gpiozero import LED, Button, AngularServo
from VirtualCopernicusNG import TkCircuit

import logging

import asyncio

import aiocoap.resource as resource
import aiocoap

import argparse

from virtual_config import configuration


class ServoResource(resource.ObservableResource):
    def __init__(self):
        super().__init__()

        self.handle = None
        self.resource = AngularServo(17, min_angle=-90, max_angle=90)
        self.resource.angle = 44

    def notify(self):
        self.updated_state()
        self.reschedule()

    def reschedule(self):
        self.handle = asyncio.get_event_loop().call_later(5, self.notify)

    def update_observation_count(self, count):
        if count and self.handle is None:
            print("Starting the clock")
            self.reschedule()
        if count == 0 and self.handle:
            print("Stopping the clock")
            self.handle.cancel()
            self.handle = None

    async def render_get(self, request):
        payload = "{}".format(self.resource.angle)
        return aiocoap.Message(payload=payload.encode())

    async def render_post(self, request):
        payload = request.payload.decode()
        print("render_post payload {}".format(payload))
        self.resource.angle = int(payload)
        return aiocoap.Message()  # TODO: return success or sth like this


# logging setup

logging.basicConfig(level=logging.INFO)
logging.getLogger("coap-server").setLevel(logging.INFO)


def virtual():
    event_loop = asyncio.get_event_loop()
    circuit = TkCircuit(configuration)

    @circuit.run
    def main():
        root = resource.Site()

        root.add_resource(['servo'], ServoResource())
        asyncio.set_event_loop(event_loop)
        asyncio.Task(aiocoap.Context.create_server_context(root))
        event_loop.run_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run CoAP server')
    parser.add_argument('device',
                        metavar='device_type',
                        type=str,
                        # nargs=1,
                        help='device',
                        choices=['gpiozero', 'virtual']
                        )

    args = parser.parse_args()

    if args.device == 'gpiozero':  # use virtual or gpiozero devices
        pass
    elif args.device == 'virtual':
        virtual()

# TODO: add proper application closing
