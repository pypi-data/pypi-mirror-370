import asyncio
import os
import time
from log.log import get_logger
from rebootdev.settings import ENVVAR_REBOOT_ENABLE_EVENT_LOOP_LAG_MONITORING
from typing import Optional

logger = get_logger(__name__)

LAG_STANDARD_HIGHWATER_SECONDS = 0.07
LAG_STANDARD_INTERVAL_SECONDS = 0.5

# A dampening factor.  When determining average calls per second or
# current lag, we weigh the current value against the previous value 2:1
# to smooth spikes.
# See https://en.wikipedia.org/wiki/Exponential_smoothing
LAG_SMOOTHING_FACTOR = 1 / 3


async def monitor_event_loop_lag(consensus_id: Optional[str] = None) -> None:
    if os.environ.get(
        ENVVAR_REBOOT_ENABLE_EVENT_LOOP_LAG_MONITORING,
        'false',
    ).lower() != 'true':
        return

    high_water = LAG_STANDARD_HIGHWATER_SECONDS
    interval = LAG_STANDARD_INTERVAL_SECONDS
    smoothing_factor = LAG_SMOOTHING_FACTOR
    current_lag = 0.0
    last_time = time.perf_counter()

    while True:
        await asyncio.sleep(interval)
        now = time.perf_counter()
        lag = now - last_time
        lag = max(0, lag - interval)
        # Dampen lag.
        current_lag = smoothing_factor * lag + (
            1 - smoothing_factor
        ) * current_lag
        last_time = now

        if current_lag > high_water:

            logger.info(
                f"Reboot event loop lag: {int(lag * 1000)}ms"
                f" {f'(consensus: {consensus_id}). ' if consensus_id else '. '}"
                "This may indicate a blocking operation on the main "
                " thread (e.g., CPU-intensive task). If you are not "
                "running such tasks, please report this issue to the "
                "maintainers."
            )
