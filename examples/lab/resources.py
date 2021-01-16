import aiocoap.resource as resource
from aiocoap import Code, Message
from gpiozero import LED, Button, AngularServo, OutputDevice, Buzzer
import asyncio

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

    def __init__(self, pin, callback_p=None, callback_r=None, loop=None):
        super().__init__()

        self.pin = pin
        self.resource = Button(pin)
        self.callback_p = callback_p
        self.callback_r = callback_r
        self.loop = loop

        self.resource.when_pressed = self.on_pressed
        self.resource.when_released = self.on_released

    def on_pressed(self):
        if self.loop:
            self.loop.call_soon_threadsafe(self.on_pressed_callback)
        else:
            asyncio.get_event_loop().call_soon_threadsafe(self.on_pressed_callback)

    def on_released(self):
        if self.loop:
            self.loop.call_soon_threadsafe(self.on_released_callback)
        else:
            asyncio.get_event_loop().call_soon_threadsafe(self.on_released_callback)

    def on_pressed_callback(self):
        self.updated_state()
        if self.callback_p:
            self.callback_p()

    def on_released_callback(self):
        self.updated_state()
        if self.callback_r:
            self.callback_r()

    def update_observation_count(self, newcount):
        super().update_observation_count(newcount)
        print(f"{self}: subscribers num: {newcount}")

    async def render_get(self, request):
        print(f'{self}: GET')
        payload = f"{self.resource.value}"
        return Message(payload=payload.encode(), code=Code.CONTENT)

    def __str__(self):
        return f"BUTTON {self.pin}"


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
