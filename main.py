import asyncio
import datetime

import aiohttp


def print_current():
    now = datetime.datetime.now()
    print(
        f"{now}\t\ttotal volume{current_volume}\t"
        f"currentvwap{current_price_times_volume / current_volume if current_volume != 0 else 0}")


async def revert(price, volume):
    global current_price_times_volume
    global current_volume
    await asyncio.sleep(time_window_seconds)
    current_price_times_volume -= price * volume
    current_volume -= volume
    print("In revert", price, volume)
    print_current()


async def process(price, volume):
    global current_price_times_volume
    global current_volume
    current_price_times_volume += price * volume
    current_volume += volume
    print("in process", price, volume)
    print_current()


async def process_and_revert(price, volume):
    asyncio.create_task(process(price, volume))
    asyncio.create_task(revert(price, volume))


async def main():
    session = aiohttp.ClientSession()
    now = datetime.datetime.now()
    async with session.ws_connect('wss://stream.binance.com:9443/ws/btcusdt@trade') as ws:
        async for msg in ws:
            rep_json = msg.json()
            asyncio.create_task(process_and_revert(price=float(rep_json['p']), volume=float(rep_json['q'])))


time_window_seconds = 60
current_price_times_volume = 0
current_volume = 0

asyncio.run(main())
