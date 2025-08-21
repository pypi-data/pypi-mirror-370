from typing import Any, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar, Type, cast
#import redis
from redis.asyncio import Redis, RedisCluster, ResponseError
import asyncio
from redis.exceptions import ConnectionError, TimeoutError
from tenacity import retry, wait_exponential, wait_fixed, stop_after_attempt, RetryError
from ewoxdbredis.clients.iredis_client import IRedisClient
from ewoxdbredis.settings.consumer_settings import ConsumerSettings
from ewoxcore.message.imessage_consumer import IMessageConsumer
from ewoxcore.message.message_args import MessageArgs
from ewoxcore.message.message_adapter import MessageAdapter

#C = TypeVar("C", redis.RedisCluster, redis.Redis)
C = TypeVar("C", RedisCluster, Redis)


class MessageStreamConsumer():
    def __init__(self, settings:ConsumerSettings, client:IRedisClient, consumer:IMessageConsumer) -> None:
        self._settings:ConsumerSettings = settings
        self._client:IRedisClient = client
        self._consumer:IMessageConsumer = consumer
        self._sem = asyncio.Semaphore(self._settings.count)



    async def subscribe(self) -> None:
        """ Subscribe to the message stream. """
        connection:C = self._client.get_connection()
        if not connection:
            raise Exception("No Redis connection available.")

        await self._create_group(connection)

        while True:
            try:
                await self._process(connection)
            # except RetryError as re:
            #     print(f"Error: Sending to dead-letter queue.")
            #     connection.xadd(DEAD_STREAM, data)
            #     connection.xack(self._settings.stream_name, self._settings.group_name, mid)
            except Exception as e:
                print("[!] Unexpected error:", e)
                await asyncio.sleep(2)


    async def _create_group(self, connection:C) -> None:
        try:
            await connection.xgroup_create(name=self._settings.stream_name, groupname=self._settings.group_name, id="0", mkstream=True)
            print(f"Created consumer group '{self._settings.group_name}' on stream '{self._settings.stream_name}'")
#        except redis.ResponseError as e:
        except ResponseError as e:
            if "BUSYGROUP" in str(e):
                print(f"Consumer group '{self._settings.group_name}' already exists.")
            else:
                raise


    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def _consume_message(self, msg_id:str, msg_data:Dict[str, Any]) -> None:
        print(f"Processing message {msg_id}: {str(msg_data)}")

        args:MessageArgs = MessageAdapter.parse(msg_data)

        await self._consumer.on_consume(
            command=args.command,
            correlation_id=args.correlationId,
            json64=args.data,
            service_name=args.serviceName)


    async def _process_message(self, connection, msg_id, msg_data):
        # Run one message under the concurrency gate
        async with self._sem:
            try:
                await self._consume_message(msg_id, msg_data)
                await self._ack_message(connection, msg_id)
            except Exception as e:
                # Write to dead letter stream
                print(f"Failed to process message {msg_id}: {e}")
                await connection.xadd(
                    f"{self._settings.stream_name}:deadletter",
                    fields={
                        "original_id": msg_id,
                        "data": str(msg_data),
                        "error": str(e),
                    },
                    maxlen=10000,  # keep only latest 10,000 entries
                    approximate=True
                )                        
                # Ack the original message
                await self._ack_message(connection, msg_id)


    @retry(
        wait=wait_exponential(min=1, max=10),
        stop=stop_after_attempt(5),
        retry_error_callback=lambda retry_state: None,
        retry=lambda retry_state: isinstance(
            retry_state.outcome.exception(),
            (ConnectionError, TimeoutError, OSError),
        )
    )
    async def _process(self, connection:C) -> None:
        results = await connection.xreadgroup(
            groupname=self._settings.group_name,
            consumername=self._settings.consumer_name,
            streams={self._settings.stream_name: '>'},
            count=self._settings.count,
            block=5000
        )

        if results:
            tasks = []
            for stream, messages in results:
                for msg_id, msg_data in messages:
                    tasks.append(asyncio.create_task(self._process_message(connection, msg_id, msg_data)))

            await asyncio.gather(*tasks)
        else:
            # If no messages were processed, check for pending messages to claim
            await self._claim_pending(connection)


    async def _process_old(self, connection:C) -> None:
        results = await connection.xreadgroup(
            groupname=self._settings.group_name,
            consumername=self._settings.consumer_name,
            streams={self._settings.stream_name: '>'},
            count=self._settings.count,
            block=5000
        )

        if results:
            for stream, messages in results:
                for msg_id, msg_data in messages:
                    try:
                        await self._process_message(connection, msg_id, msg_data)
                        await self._ack_message(connection, msg_id)
                    except Exception as e:
                        print(f"Failed to process message {msg_id}: {e}")
                        
                        # Write to dead letter stream
                        await connection.xadd(
                            f"{self._settings.stream_name}:deadletter",
                            fields={
                                "original_id": msg_id,
                                "data": str(msg_data),
                                "error": str(e),
                            },
                            maxlen=10000,  # keep only latest 10,000 entries
                            approximate=True
                        )                        
                        # Ack the original message
                        await self._ack_message(connection, msg_id)
        else:
            # If no messages were processed, check for pending messages to claim
            await self._claim_pending(connection)


    async def _ack_message(self, connection:C, msg_id:str) -> None:
        """ Acknowledge a message in the stream. """
        await connection.xack(self._settings.stream_name, self._settings.group_name, msg_id)
        if (self._settings.deleteAfterAck):
            await connection.xdel(self._settings.stream_name, msg_id)


    async def _claim_pending(self, connection:C) -> None:
        """ Claim pending messages from failed consumers older than X seconds. """
        claim_after_ms: int = self._settings.claim_after_seconds * 1000
        start_id = "0-0"

        while True:
            next_id, claimed, *_ = await connection.xautoclaim(
                self._settings.stream_name,
                self._settings.group_name,
                self._settings.consumer_name,
                min_idle_time=claim_after_ms,
                start_id=start_id,
                count=100,
            )

            for mid, data in claimed:
                await self._process_message(connection, mid, data)
                await connection.xack(self._settings.stream_name, self._settings.group_name, mid)

            if not claimed:
                break

            start_id = next_id


"""
import asyncio
from contextlib import suppress

class Consumer:
    def __init__(self, settings, max_concurrency: int = 20):
        self._settings = settings
        self._sem = asyncio.Semaphore(max_concurrency)

    async def _handle_one(self, connection, msg_id, msg_data):
        # Run one message under the concurrency gate
        async with self._sem:
            try:
                await self.process_message(msg_id, msg_data)
                self._ack_message(connection, msg_id)
            except Exception as e:
                # Log + dead-letter then ack original, same as before
                print(f"Failed to process message {msg_id}: {e}")
                connection.xadd(
                    f"{self._settings.stream_name}:deadletter",
                    fields={
                        "original_id": msg_id,
                        "data": str(msg_data),
                        "error": str(e),
                    },
                    maxlen=10000,
                    approximate=True,
                )
                self._ack_message(connection, msg_id)

    async def _process(self, connection) -> None:
        #Read in batches; process each message concurrently.
        while True:
            # If you're using redis.asyncio, this call should be awaited.
            # If it's a sync client, it will block the loop — consider switching to redis.asyncio (see note below).
            results = connection.xreadgroup(
                groupname=self._settings.group_name,
                consumername=self._settings.consumer_name,
                streams={self._settings.stream_name: '>'},
                count=10,
                block=5000,  # 5s long-poll
            )

            if results:
                tasks = []
                for stream, messages in results:
                    for msg_id, msg_data in messages:
                        tasks.append(asyncio.create_task(self._handle_one(connection, msg_id, msg_data)))

                # Let the whole batch run concurrently; exceptions are handled in _handle_one
                # so we don't need return_exceptions=True.
                # If you prefer to keep reading new batches while the current batch runs,
                # you can omit this await (but then track outstanding tasks to avoid unbounded growth).
                await asyncio.gather(*tasks)
            else:
                # No new messages — try to claim pending
                await self._claim_pending(connection)

"""