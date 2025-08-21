import asyncio


async def execute(args):
    # 异步执行
    print(args)
    i = 1 / 0
    for i in range(20):
        print(i)
        await asyncio.sleep(1)
    return {
        "a": 1,
        "b": 2,
        "c": 3,
    }
