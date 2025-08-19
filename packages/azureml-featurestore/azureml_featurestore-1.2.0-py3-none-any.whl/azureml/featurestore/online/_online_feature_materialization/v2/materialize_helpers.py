# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# cspell: ignore coro, evals, unclustered

import asyncio
import datetime
import os
import time
from typing import (
    Any,
    Callable,
    Iterable,
    List,
    Tuple,
)

from azure.core.credentials import TokenCredential
from azureml.featurestore._utils._constants import (
    AZUREML_ONLINE_MATERIALIZATION_BATCH_SIZE,
    AZUREML_ONLINE_MATERIALIZATION_MAX_ATTEMPTS,
    AZUREML_ONLINE_MATERIALIZATION_EVALS_PER_TASK_PER_SECOND
)
from azureml.featurestore.online._redis_client_pool import _get_redis_connection_string

from redis import Redis
from redis.cluster import RedisCluster

__REDIS_SLOT_COUNT = 16384

__DEFAULT_UNCLUSTERED_BATCH_SIZE = 256
__DEFAULT_CLUSTERED_BATCH_SIZE = 16


def get_mapper(
        redis_resource_id: str,
        lua_script: str,
        record_serializer: Callable[[Any], Tuple[str, int, bytes]],
        credential: TokenCredential) -> Callable[[int, Iterable[Any]], Iterable[int]]:
    redis_connection_string, clustering_enabled = _get_redis_connection_string(redis_resource_id, credential)
    def mapper(partition_index: int, records: Iterable[Any]) -> Iterable[int]:
        materialization_batch_size = int(os.environ[AZUREML_ONLINE_MATERIALIZATION_BATCH_SIZE]) \
            if AZUREML_ONLINE_MATERIALIZATION_BATCH_SIZE in os.environ else None

        max_materialization_attempts = int(os.environ[AZUREML_ONLINE_MATERIALIZATION_MAX_ATTEMPTS]) \
            if AZUREML_ONLINE_MATERIALIZATION_MAX_ATTEMPTS in os.environ else 3

        delay_seconds_between_materialization_evals = 1.0 / (
            float(os.environ[AZUREML_ONLINE_MATERIALIZATION_EVALS_PER_TASK_PER_SECOND]) \
                if AZUREML_ONLINE_MATERIALIZATION_EVALS_PER_TASK_PER_SECOND in os.environ else 100.0
            )

        if clustering_enabled:
            # Initialize a RedisCluster client
            redis_client = RedisCluster.from_url(redis_connection_string)
            materialization_function = redis_client.register_script(lua_script)
            batch_size = materialization_batch_size or __DEFAULT_CLUSTERED_BATCH_SIZE

            queues = [asyncio.Queue(maxsize=4 * batch_size) for _ in range(__REDIS_SLOT_COUNT)]
            def queue_indexer(key: str) -> int:
                # In a clustered Redis setup, we can use the hash slot to determine the queue index
                return redis_client.keyslot(key)
        else:
            # Initialize a regular Redis client
            redis_client = Redis.from_url(redis_connection_string)
            materialization_function = redis_client.register_script(lua_script)
            batch_size = materialization_batch_size or __DEFAULT_UNCLUSTERED_BATCH_SIZE

            queues = [asyncio.Queue(maxsize=4 * batch_size)]
            def queue_indexer(_: str) -> int:
                # In a non-clustered Redis setup, we just use a single queue
                return 0

        if delay_seconds_between_materialization_evals > 0:
            print(
                f"[OnlineMaterialization Partition {partition_index} @ {datetime.datetime.now(datetime.timezone.utc)}]"
                f" Using throttled materialization with a delay of {delay_seconds_between_materialization_evals} "
                f"seconds between evaluations.")

            materialization_lock = asyncio.Lock()
            last_materialization_time = time.time()
            async def thr_materialization_function(keys: List[str], args: List[bytes]) -> int:
                nonlocal last_materialization_time, materialization_lock
                async with materialization_lock:
                    elapsed_time = time.time() - last_materialization_time
                    if elapsed_time < delay_seconds_between_materialization_evals:
                        await asyncio.sleep(delay_seconds_between_materialization_evals - elapsed_time)

                    last_materialization_time = time.time()
                    return materialization_function(keys=keys, args=args)
        else:
            print(
                f"[OnlineMaterialization Partition {partition_index} @ {datetime.datetime.now(datetime.timezone.utc)}]"
                f"Using immediate materialization without throttling.")
            async def thr_materialization_function(keys: List[str], args: List[bytes]) -> int:
                return materialization_function(keys=keys, args=args)

        async def coro():
            queue_shutdown = asyncio.Event()

            producer_future = asyncio.gather(
                _producer(queues, records, record_serializer, queue_indexer, partition_index)
            )
            consumer_futures = asyncio.gather(
                *[_consumer(
                    queues[i],
                    batch_size,
                    thr_materialization_function,
                    partition_index,
                    i,
                    queue_shutdown,
                    max_materialization_attempts)
                  for i in range(len(queues))]
            )

            producer_result = await producer_future
            queue_shutdown.set()
            consumer_results = await consumer_futures
            processed_records, materialized_records = zip(*consumer_results)

            return (sum(producer_result), sum(processed_records), sum(materialized_records))

        (total_records_produced, total_records_processed, total_records_materialized) = asyncio.run(coro())

        if total_records_produced != total_records_processed:
            raise Exception(
                f"Producer thread processed {total_records_produced} records, but only {total_records_processed}"
                f" records were seen by the consumer threads. This is unexpected and indicates a bug in the code.")

        print(
            f"[OnlineMaterialization Partition {partition_index} @ {datetime.datetime.now(datetime.timezone.utc)}]"
            f" Processed {total_records_processed} records, and materialized {total_records_materialized} "
            f"records to redis.")

        yield total_records_materialized

    return mapper


async def _consumer(
        consumer_queue: asyncio.Queue,
        batch_size: int,
        materialization_function: Callable[[List[str], List[bytes]], int],
        partition_index: int,
        consumer_index: int,
        queue_shutdown: asyncio.Event,
        max_materialization_attempts: int):
    start_time = time.time()
    total_processed_records = 0
    total_materialized_records = 0
    batch_count = 0
    keyslist = []
    argslist = []

    async def send_batch():
        nonlocal total_processed_records, total_materialized_records, batch_count, keyslist, argslist
        exceptions = []
        for _attempt in range(max_materialization_attempts):
            try:
                num_records_added = await materialization_function(keys=keyslist, args=argslist)
                total_processed_records += len(keyslist)
                total_materialized_records += num_records_added

                keyslist = []
                argslist = []
                batch_count += 1
                return
            except Exception as e: # pylint: disable=broad-except
                print(
                    f"[OnlineMaterialization Partition {partition_index} Consumer {consumer_index} @ "
                    f"{datetime.datetime.now(datetime.timezone.utc)}] Error occurred when materializing"
                    f" batch {batch_count}: {e}")
                exceptions.append(e)
                await asyncio.sleep(3)

        # If we get here, it means we failed to materialize the batch after max_materialization_attempts attempts
        print(
            f"[OnlineMaterialization Partition {partition_index} Consumer {consumer_index} @ "
            f"{datetime.datetime.now(datetime.timezone.utc)}] Failed to materialize batch {batch_count} "
            f"after {max_materialization_attempts} attempts.")
        raise Exception(
            f"Failed to materialize batch {batch_count} after {max_materialization_attempts} attempts."
        ) from exceptions[-1]


    while True:
        if len(keyslist) >= batch_size:
            await send_batch()

        if queue_shutdown.is_set():
            if consumer_queue.empty():
                # queue_shutdown is set and the queue is empty. We can guarantee that no more records will
                # be added to the queue after the shutdown event, so we can break out of the consumer loop.
                break

            # queue_shutdown is set, but the queue is not empty. Drain whatever records remain.
            task_queue_get = asyncio.create_task(consumer_queue.get())
            await asyncio.wait(
                [task_queue_get],
                return_when=asyncio.FIRST_COMPLETED
            )
        else:
            # queue_shutdown is not set, so wait for either a new record to be added to the queue, or for
            # the shutdown event to be set.
            task_queue_get = asyncio.create_task(consumer_queue.get())
            task_event_get = asyncio.create_task(queue_shutdown.wait())

            await asyncio.wait(
                [task_queue_get, task_event_get],
                return_when=asyncio.FIRST_COMPLETED
            )

            if not task_queue_get.done():
                continue

        (key, timestamp, data) = task_queue_get.result()

        keyslist.append(key)
        argslist.append(timestamp)
        argslist.append(data)

    if len(keyslist) > 0:
        # Send the last (potentially incomplete) batch
        await send_batch()

    consumer_latency = time.time() - start_time
    print(
        f"[OnlineMaterialization Partition {partition_index} Consumer {consumer_index} @ "
        f"{datetime.datetime.now(datetime.timezone.utc)}] Consumer thread finished in {consumer_latency}"
        f" seconds, processed {total_processed_records} records and materialized {total_materialized_records}"
        f" records in {batch_count} batches.")
    return total_processed_records, total_materialized_records


async def _producer(
        queues: List[asyncio.Queue],
        records: Iterable[Any],
        record_serializer: Callable[[Any], Tuple[str, int, bytes]],
        queue_indexer: Callable[[str], int],
        partition_index: int) -> int:
    print(
        f"[OnlineMaterialization Partition {partition_index} @ {datetime.datetime.now(datetime.timezone.utc)}]"
        f" Starting producer thread.")
    num_records_processed = 0

    for record in records:
        key, timestamp, data = record_serializer(record)
        queue_index = queue_indexer(key)
        await queues[queue_index].put((key, timestamp, data))
        num_records_processed += 1

    print(
        f"[OnlineMaterialization Partition {partition_index} @ {datetime.datetime.now(datetime.timezone.utc)}]"
        f" Producer thread finished, processed {num_records_processed} records.")
    return num_records_processed
