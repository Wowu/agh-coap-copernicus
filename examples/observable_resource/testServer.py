import asyncio
import random

import aiocoap
import aiocoap.resource as resource


class TemperatureResource(resource.ObservableResource):
    def __init__(self):
        super(TemperatureResource, self).__init__()
        self.temp = {'temperature': None, 'units': None}
        self.notify()  # start monitoring resource state

    def current_temperature(self):
        return random.randint(0, 30)

    def notify(self):
        new_temp = self.current_temperature()
        self.temp = new_temp
        self.updated_state()  # inform subscribers

        # check again after 5 seconds
        asyncio.get_event_loop().call_later(3, self.notify)

    def update_observation_count(self, newcount):
        print(f"newcount {newcount}")
        self.updated_state()

    async def render_get(self, request):
        print(f'Render get requested {self.temp}')
        mesg = aiocoap.Message(code=aiocoap.CONTENT,
                               payload=str(self.temp).encode())
        return mesg


def main():
    # Resource tree creation
    root = resource.Site()

    root.add_resource(('temperature',), TemperatureResource())

    asyncio.ensure_future(aiocoap.Context.create_server_context(root, bind=("127.0.0.1", 5683)))
    asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    main()
