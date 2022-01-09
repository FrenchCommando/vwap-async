import datetime
import asyncio


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
    now = datetime.datetime.now()
    print(now)
    asyncio.create_task(process_and_revert(price=100, volume=1))
    await asyncio.sleep(2)
    asyncio.create_task(process_and_revert(price=200, volume=3))
    await asyncio.sleep(9)
    asyncio.create_task(process_and_revert(price=500, volume=2))
    await asyncio.sleep(15)


time_window_seconds = 10
current_price_times_volume = 0
current_volume = 0

asyncio.run(main())
