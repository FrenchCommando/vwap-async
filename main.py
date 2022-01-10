import asyncio
import datetime
import aiohttp


def print_current():
    now = datetime.datetime.now()
    print(
        f"{now}\t\ttotal volume\t{current_volume:.8f}\t\t"
        f"currentvwap\t\t{current_price_times_volume / current_volume if current_volume != 0 else 0:.2f}"
    )


def revert(price, volume):
    global current_price_times_volume
    global current_volume
    current_price_times_volume -= price * volume
    current_volume -= volume
    # print("\t\t\t\t\t\tIn revert", price, volume)
    print_current()


def process(price, volume):
    global current_price_times_volume
    global current_volume
    current_price_times_volume += price * volume
    current_volume += volume
    # print("\t\t\t\t\t\tIn process", price, volume)
    print_current()


async def process_and_revert(price, volume):
    process(price, volume)
    asyncio.get_event_loop().call_later(time_window_seconds, revert, price, volume)


async def main_binance():
    session = aiohttp.ClientSession()
    async with session.ws_connect('wss://stream.binance.com:9443/ws/btcusdt@trade') as ws:
        async for msg in ws:
            rep_json = msg.json()
            asyncio.create_task(process_and_revert(
                price=float(rep_json['p']), volume=float(rep_json['q'])
            ))


async def main_short():
    asyncio.create_task(process_and_revert(price=100, volume=1))
    await asyncio.sleep(3)
    asyncio.create_task(process_and_revert(price=200, volume=3))
    await asyncio.sleep(10)


if __name__ == '__main__':
    current_price_times_volume = 0
    current_volume = 0
    short_only = False
    if short_only:
        time_window_seconds = 5
        asyncio.run(main_short())
    else:
        time_window_seconds = 60
        asyncio.run(main_binance())
