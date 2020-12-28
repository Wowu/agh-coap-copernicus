#!/usr/bin/env python3

from gpiozero import LED, Button, AngularServo
from VirtualCopernicusNG import TkCircuit

import logging

import asyncio

import aiocoap.resource as resource
from aiocoap import Code, Context, Message

import argparse

from virtual_config import configuration


class ServoResource(resource.Resource):

    def get_link_description(self):
        # Publish additional data in .well-known/core
        return dict(**super().get_link_description(), title=f"Servo Resource - pin: {self.pin}")

    def __init__(self, pin, min_angle=-90, max_angle=90, default_angle=0):
        super().__init__()

        self.handle = None

        self.pin = pin
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.resource = AngularServo(pin, min_angle=min_angle, max_angle=max_angle)
        self.resource.angle = default_angle

    async def render_get(self, request):
        payload = f"{self.resource.angle}";
        return Message(payload=payload.encode(), code=Code.CONTENT)

    async def render_post(self, request):
        payload = request.payload.decode()
        print(f"render_post payload {payload}")
        if self.min_angle <= int(payload) <= self.max_angle:
            self.resource.angle = int(payload)
            return Message(code=Code.CHANGED)
        else:
            return Message(code=Code.BAD_REQUEST)


class LEDResource(resource.Resource):

    def get_link_description(self):
        # Publish additional data in .well-known/core
        return dict(**super().get_link_description(), title=f"LED Resource - pin: {self.pin}")

    def __init__(self, pin):
        super().__init__()

        self.handle = None

        self.pin = pin
        self.resource = LED(pin)

    async def render_get(self, request):
        payload = f"{self.resource.value}";
        return Message(payload=payload.encode(), code=Code.CONTENT)

    async def render_post(self, request):
        payload = request.payload.decode()
        print(f"render_post payload {payload}")
        new_state = int(payload)
        if new_state == 0:
            self.resource.off()
        elif new_state == 1:
            self.resource.on()
        else:
            return Message(code=Code.BAD_REQUEST)
        return Message(code=Code.CHANGED)



class BuzzerResource(resource.Resource):

    def get_link_description(self):
        # Publish additional data in .well-known/core
        return dict(**super().get_link_description(), title=f"Buzzer Resource - pin: {self.pin}")

    def __init__(self, pin):
        super().__init__()

        self.handle = None

        self.pin = pin
        self.resource = LED(pin)

    async def render_get(self, request):
        payload = f"{self.resource.value}";
        return Message(payload=payload.encode(), code=Code.CONTENT)

    async def render_post(self, request):
        payload = request.payload.decode()
        print(f"render_post payload {payload}")
        new_state = int(payload)
        if new_state == 0:
            self.resource.off()
        elif new_state == 1:
            self.resource.on()
        else:
            return Message(code=Code.BAD_REQUEST)
        return Message(code=Code.CHANGED)


# logging setup

logging.basicConfig(level=logging.INFO)
logging.getLogger("coap-server").setLevel(logging.INFO)


def virtual():
    event_loop = asyncio.get_event_loop()
    circuit = TkCircuit(configuration)

    @circuit.run
    def main():
        root = resource.Site()
        root.add_resource(['.well-known', 'core'],
                          resource.WKCResource(root.get_resources_as_linkheader))
        root.add_resource(['servo'], ServoResource(17))
        root.add_resource(['led1'], LEDResource(21))
        root.add_resource(['led2'], LEDResource(22))
        root.add_resource(['buzzer'], BuzzerResource(16))
        asyncio.set_event_loop(event_loop)
        asyncio.Task(Context.create_server_context(root, bind=("127.0.0.1", 5683)))
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
