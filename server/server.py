#!/usr/bin/env python3
import argparse
import logging
import asyncio

from gpiozero import LED, Button, AngularServo, OutputDevice, Buzzer
import aiocoap.resource as resource
from aiocoap import Code, Context, Message

from VirtualCopernicusNG import TkCircuit
from virtual_config import configuration

# logging setup
logging.basicConfig(level=logging.INFO)
logging.getLogger("coap-server").setLevel(logging.INFO)

SERVER_IP = '0.0.0.0'


class ServoResource(resource.Resource):
    def get_link_description(self):
        # Publish additional data in .well-known/core
        return dict(**super().get_link_description(), title=f"Servo Resource - pin: {self.pin}")

    def __init__(self, pin, min_angle=-90, max_angle=90, default_angle=0):
        super().__init__()

        self.pin = pin
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.resource = AngularServo(pin, min_angle=min_angle, max_angle=max_angle)
        self.resource.angle = default_angle

    async def render_get(self, request):
        print(f'SERVO {self.pin}: GET')
        payload = f"{self.resource.angle}"
        return Message(payload=payload.encode(), code=Code.CONTENT)

    async def render_post(self, request):
        payload = request.payload.decode()
        print(f'SERVO {self.pin}: POST {payload}')
        if self.min_angle <= int(payload) <= self.max_angle:
            self.resource.angle = int(payload)
            return Message(code=Code.CHANGED)

        return Message(code=Code.BAD_REQUEST)


class LEDResource(resource.Resource):
    def get_link_description(self):
        # Publish additional data in .well-known/core
        return dict(**super().get_link_description(), title=f"LED Resource - pin: {self.pin}")

    def __init__(self, pin):
        super().__init__()

        self.pin = pin
        self.resource = LED(pin)

    async def render_get(self, request):
        payload = f"{self.resource.value}"
        print(f'LED {self.pin}: GET')
        return Message(payload=payload.encode(), code=Code.CONTENT)

    async def render_post(self, request):
        payload = request.payload.decode()
        print(f'LED {self.pin}: POST {payload}')

        if payload in ['0', 'off']:
            self.resource.off()
        elif payload in ['1', 'on']:
            self.resource.on()
        elif payload in ['-1', 'toggle']:
            self.resource.toggle()
        elif 'blink' in payload:
            p = payload.split(" ")
            if p[0] != 'blink':
                return Message(code=Code.BAD_REQUEST)

            on_time, off_time, n = 1, 1, None
            if len(p) > 1 and p[1].isdigit():
                on_time = int(p[1])
            if len(p) > 2 and p[2].isdigit():
                off_time = int(p[2])
            if len(p) > 3 and p[3].isdigit():
                n = int(p[3])

            self.resource.blink(on_time, off_time, n)
        else:
            return Message(code=Code.BAD_REQUEST)
        return Message(code=Code.CHANGED)

class GPIOResource(resource.Resource):
    def get_link_description(self):
        # Publish additional data in .well-known/core
        return dict(**super().get_link_description(), title=f"GPIO Resource - pin: {self.pin}")

    def __init__(self, pin):
        super().__init__()

        self.pin = pin
        self.resource = OutputDevice(pin)

    async def render_get(self, request):
        print(f'GPIO {self.pin}: GET')
        payload = f"{self.resource.value}"
        return Message(payload=payload.encode(), code=Code.CONTENT)

    async def render_post(self, request):
        payload = request.payload.decode()
        print(f'GPIO {self.pin}: POST {payload}')

        if payload in ['0', 'off']:
            self.resource.off()
        elif payload in ['1', 'on']:
            self.resource.on()
        else:
            return Message(code=Code.BAD_REQUEST)
        return Message(code=Code.CHANGED)


class ButtonResource(resource.ObservableResource):
    global event_loop

    def get_link_description(self):
        # Publish additional data in .well-known/core
        return dict(**super().get_link_description(), title=f"Button Resource - pin: {self.pin}")

    def __init__(self, pin, callback_p=None, callback_r=None):
        super().__init__()

        self.pin = pin
        self.resource = Button(pin)
        self.callback_p = callback_p
        self.callback_r = callback_r

        self.resource.when_pressed = self.on_pressed
        self.resource.when_released = self.on_released

    def on_pressed(self):
        event_loop.call_soon_threadsafe(self.on_pressed_callback)

    def on_released(self):
        event_loop.call_soon_threadsafe(self.on_released_callback)

    def on_pressed_callback(self):
        self.updated_state()
        if self.callback_p:
            self.callback_p()

    def on_released_callback(self):
        self.updated_state()
        if self.callback_r:
            self.callback_r()

    async def render_get(self, request):
        print(f'BUTTON {self.pin}: GET')
        payload = f"{self.resource.value}"
        return Message(payload=payload.encode(), code=Code.CONTENT)


class BuzzerResource(resource.Resource):
    def get_link_description(self):
        # Publish additional data in .well-known/core
        return dict(**super().get_link_description(), title=f"Buzzer Resource - pin: {self.pin}")

    def __init__(self, pin, active_high=True, initial_value=False):
        super().__init__()

        self.pin = pin
        self.resource = Buzzer(pin, active_high=active_high, initial_value=initial_value)

    async def render_get(self, request):
        payload = f"{self.resource.value}"
        print(f'BUZZER {self.pin}: GET')
        return Message(payload=payload.encode(), code=Code.CONTENT)

    async def render_post(self, request):
        payload = request.payload.decode()
        print(f'BUZZER {self.pin}: POST {payload}')
        if payload in ['0', 'off']:
            self.resource.off()
        elif payload in ['1', 'on']:
            self.resource.on()
        elif payload in ['-1', 'toggle']:
            self.resource.toggle()
        elif 'beep' in payload:
            p = payload.split(" ")
            if p[0] != 'beep':
                return Message(code=Code.BAD_REQUEST)

            on_time, off_time, n = 1, 1, None
            if len(p) > 1 and p[1].isdigit():
                on_time = int(p[1])
            if len(p) > 2 and p[2].isdigit():
                off_time = int(p[2])
            if len(p) > 3 and p[3].isdigit():
                n = int(p[3])

            self.resource.beep(on_time, off_time, n)
        else:
            return Message(code=Code.BAD_REQUEST)
        return Message(code=Code.CHANGED)

def virtual():
    """Simulate coap resources in VirtualCopernicus"""
    circuit = TkCircuit(configuration)

    @circuit.run
    def main():
        root = resource.Site()
        root.add_resource(['.well-known', 'core'],
                          resource.WKCResource(root.get_resources_as_linkheader))
        root.add_resource(['servo'], ServoResource(17))
        root.add_resource(['led1'], LEDResource(21))
        root.add_resource(['led2'], LEDResource(22))
        root.add_resource(['button1'], ButtonResource(11, lambda: print("Button1 pressed")))
        root.add_resource(['button2'], ButtonResource(12))
        root.add_resource(['buzzer'], BuzzerResource(16))
        root.add_resource(['gpio_buzzer'], GPIOResource(15))
        asyncio.set_event_loop(event_loop)
        asyncio.Task(Context.create_server_context(root, bind=(SERVER_IP, 5683)))
        event_loop.run_forever()


def physical():
    """Run coap resources on real raspberry pi"""
    root = resource.Site()
    root.add_resource(['.well-known', 'core'],
                      resource.WKCResource(root.get_resources_as_linkheader))
    root.add_resource(['led'], LEDResource(17))
    root.add_resource(['buzzer'], BuzzerResource(22, active_high=False, initial_value=True))
    root.add_resource(['button'], ButtonResource(27, lambda: print("Button pressed")))

    asyncio.set_event_loop(event_loop)
    asyncio.Task(Context.create_server_context(root, bind=(SERVER_IP, 5683)))
    event_loop.run_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run CoAP server')
    parser.add_argument('device', metavar='device_type', type=str,
                        help='device', choices=['gpiozero', 'virtual'])
    parser.add_argument('address', nargs='?', metavar='server_address', type=str,
                        help='CoAP server address', default="0.0.0.0")

    args = parser.parse_args()
    SERVER_IP = args.address
    event_loop = asyncio.get_event_loop()

    # use virtual or gpiozero devices
    if args.device == 'gpiozero':
        physical()
    elif args.device == 'virtual':
        virtual()

