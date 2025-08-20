import asyncio

async def task():
    print("task...")
    await asyncio.sleep(10)

async def main():
    t = asyncio.create_task(task())
    await asyncio.sleep(0.1)
    t.cancel()
    print("task.canceled.")
#Task was destroyed but it is pending!
asyncio.run( main())