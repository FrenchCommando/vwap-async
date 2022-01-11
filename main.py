import aiohttp
import asyncio
import datetime


class VWAP:
    def __init__(self, time_window_seconds):
        self.current_price_times_volume = 0
        self.current_volume = 0
        self.time_window_seconds = time_window_seconds

    def print_current(self):
        now = datetime.datetime.now()
        print(
            f"{now}\t\ttotal volume\t{self.current_volume:.8f}\t\t"
            f"currentvwap\t\t"
            f"{self.current_price_times_volume / self.current_volume if self.current_volume != 0 else 0:.2f}"
        )

    def revert(self, price, volume):
        self.current_price_times_volume -= price * volume
        self.current_volume -= volume
        # print("\t\t\t\t\t\tIn revert", price, volume)
        self.print_current()

    def process(self, price, volume):
        self.current_price_times_volume += price * volume
        self.current_volume += volume
        # print("\t\t\t\t\t\tIn process", price, volume)
        self.print_current()

    async def process_and_revert(self, price, volume):
        self.process(price, volume)
        asyncio.get_event_loop().call_later(self.time_window_seconds, self.revert, price, volume)


async def main_binance():
    session = aiohttp.ClientSession()
    async with session.ws_connect('wss://stream.binance.com:9443/ws/btcusdt@trade') as ws:
        vwap = VWAP(time_window_seconds=60)
        async for msg in ws:
            rep_json = msg.json()
            asyncio.create_task(vwap.process_and_revert(
                price=float(rep_json['p']), volume=float(rep_json['q'])
            ))


async def main_short():
    vwap = VWAP(time_window_seconds=5)
    asyncio.create_task(vwap.process_and_revert(price=100, volume=1))
    await asyncio.sleep(3)
    asyncio.create_task(vwap.process_and_revert(price=200, volume=3))
    await asyncio.sleep(10)


def main():
    short_only = False
    if short_only:
        asyncio.run(main_short())
    else:
        asyncio.run(main_binance())


if __name__ == '__main__':
    main()
