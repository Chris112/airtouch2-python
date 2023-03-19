from typing import Callable
from airtouch2.at2plus.AT2PlusAircon import At2PlusAircon
from airtouch2.at2plus.AT2PlusClient import At2PlusClient
import logging
import asyncio
import aioconsole
logging.basicConfig(filename='airtouch2plus.log',filemode='a', level=logging.DEBUG, format='%(asctime)s %(threadName)s %(levelname)s: %(message)s')
_LOGGER = logging.getLogger()
_LOGGER.addHandler(logging.StreamHandler())
logging.getLogger('asyncio').setLevel(logging.WARNING)

class AcStatusPrinter:
    client: At2PlusClient
    acs: list[At2PlusAircon]
    cleanup_callbacks: list[Callable]
    def __init__(self, client: At2PlusClient):
        self.cleanup_callbacks.append(client.add_new_ac_callback(self.new_ac))

    def new_ac(self):
        for ac in self.client.aircons_by_id.values():
            if ac not in self.acs:
                self.acs.append(ac)
                print(ac.status)
                print(ac.ability)
                self.cleanup_callbacks.append(ac.add_callback(lambda : print(ac.status)))

    def cleanup(self):
        while len(self.cleanup_callbacks) > 0:
            self.cleanup_callbacks.pop()()

async def main():
    addr = await aioconsole.ainput("Enter airtouch2plus IP address: ")
    client = At2PlusClient(addr, dump=True)
    if not await client.connect():
        raise RuntimeError(f"Could not connect to {client._host_ip}:{client._host_port}")
    printer = AcStatusPrinter(client)
    await client.run()
    inp = await aioconsole.ainput("Enter 'q' to quit: ")
    while inp != "q":
        inp = await aioconsole.ainput("Enter 'q' to quit: ")
    await client.stop()
    printer.cleanup()

asyncio.run(main())
