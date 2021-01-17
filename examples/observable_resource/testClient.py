#!/usr/bin/env python3

import asyncio

from aiocoap import *

CONTENT_FORMAT_CBOR = 60


async def main():
    protocol = await Context.create_client_context()

    request = Message(code=GET, uri='coap://[127.0.0.1]/temperature', observe=0)

    pr = protocol.request(request)

    # Note that it is necessary to start sending
    r = await pr.response

    async for r in pr.observation:
        print("New temperature: %r" % r.payload)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
