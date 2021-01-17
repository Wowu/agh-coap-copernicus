import asyncio
from time import sleep

from aiocoap import Context, Message, Code
from gpiozero import Button

SERVER_IP = "172.16.0.111"

def format_response(code, payload):
    print(f"Response: {code}")
    if len(payload) > 0:
        print(payload.decode('utf-8'))


async def send_by_coap(name: str, val: str):
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
        print(e)


def button_pressed():
    event_loop.run_until_complete(send_by_coap("led1", "toggle"))


event_loop = asyncio.new_event_loop()
asyncio.set_event_loop(event_loop)

button = Button(27)
button.when_pressed = button_pressed

while True:
    sleep(0.1)


