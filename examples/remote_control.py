import asyncio
import aiocoap
from aiocoap import Context, Message, Code

@asyncio.coroutine
def start_server():
    protocol = yield from Context.create_client_context()

    request = Message(code = Code.GET, mtype=aiocoap.CON)
    request.set_request_uri('coap://127.0.0.1/button')
    # set observe bit from None to 0
    request.opt.observe = 0

    def handle_notification(response):
        print("asdsadsa")
        print(response)
        import code; code.interact(local=dict(globals(), **locals()))

    protocol_request = protocol.request(request)
    protocol_request.observation.register_callback(handle_notification)
    protocol_request.observation.register_errback(handle_notification)
    response = yield from protocol_request.response


event_loop = asyncio.new_event_loop()
asyncio.set_event_loop(event_loop)
event_loop.create_task(start_server())
asyncio.get_event_loop().run_forever()
