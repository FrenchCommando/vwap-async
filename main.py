import aiohttp
import asyncio
import datetime


class VWAP:
    def __init__(self, time_window_seconds):
        self.current_price_times_volume = 0
        self.current_volume = 0
        self.current_volume_buy = 0
        self.current_volume_sell = 0
        self.time_window_seconds = time_window_seconds

    def print_current(self):
        now = datetime.datetime.now()
        print(
            f"{now}\t\t"
            f"volume\t{self.current_volume:.5f}\t\t"
            f"price\t{self.current_price():.2f}\t\t"
            f"buyVolume\t{self.current_volume_buy:.5f}\t\t"
            f"sellVolume\t{self.current_volume_sell:.5f}"
        )

    def current_price(self):
        return self.current_price_times_volume / self.current_volume if self.current_volume != 0 else 0

    def revert(self, price, volume, sell):
        self.current_price_times_volume -= price * volume
        self.current_volume -= volume
        if sell:
            self.current_volume_sell -= volume
        else:
            self.current_volume_buy -= volume
        # print("\t\t\t\t\t\tIn revert", price, volume)
        self.print_current()

    def process(self, price, volume, sell):
        self.current_price_times_volume += price * volume
        self.current_volume += volume
        if sell:
            self.current_volume_sell += volume
        else:
            self.current_volume_buy += volume
        # print("\t\t\t\t\t\tIn process", price, volume)
        self.print_current()

    async def process_and_revert(self, price, volume, sell):
        self.process(price, volume, sell)
        asyncio.get_event_loop().call_later(self.time_window_seconds, self.revert, price, volume, sell)


async def main_binance():
    session = aiohttp.ClientSession()
    async with session.ws_connect('wss://stream.binance.com:9443/ws/btcusdt@trade') as ws:
        vwap = VWAP(time_window_seconds=60)
        async for msg in ws:
            rep_json = msg.json()
            # print(rep_json)
            asyncio.create_task(vwap.process_and_revert(
                price=float(rep_json['p']), volume=float(rep_json['q']), sell=bool(rep_json['m'])
            ))


async def main_short():
    vwap = VWAP(time_window_seconds=5)
    asyncio.create_task(vwap.process_and_revert(price=100, volume=1, sell=True))
    await asyncio.sleep(3)
    asyncio.create_task(vwap.process_and_revert(price=200, volume=3, sell=False))
    await asyncio.sleep(10)


def main():
    short_only = False
    if short_only:
        asyncio.run(main_short())
    else:
        asyncio.run(main_binance())


if __name__ == '__main__':
    main()
