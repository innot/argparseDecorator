#  Copyright (c) 2022 Thomas Holland
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see the accompanying LICENSE.txt file or
#  go to <https://opensource.org/licenses/MIT>.
#

import asyncio
import time

from argparsedecorator import *

cli = ArgParseDecorator()


@cli.command
async def sleep(n: float):
    """Sleep for n duration.
    :param n: number of duration to sleep (float)
    """
    print("start sleeping")
    t_start = time.time()
    await asyncio.sleep(n)
    t_end = time.time()
    print(f"woke up after {round(t_end - t_start, 3)} seconds")


async def runner():
    await cli.execute_async("sleep 1.5")


if __name__ == "__main__":
    asyncio.run(runner())
