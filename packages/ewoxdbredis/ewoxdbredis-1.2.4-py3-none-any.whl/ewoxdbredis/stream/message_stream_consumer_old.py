from typing import Any, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar, Type, cast
import redis
import asyncio
from redis.exceptions import ConnectionError, TimeoutError
from tenacity import retry, wait_exponential, wait_fixed, stop_after_attempt, RetryError
from ewoxdbredis.clients.iredis_client import IRedisClient
from ewoxdbredis.settings.consumer_settings import ConsumerSettings
from ewoxcore.message.imessage_consumer import IMessageConsumer
from ewoxcore.message.message_args import MessageArgs

C = TypeVar("C", redis.RedisCluster, redis.Redis)


class MessageStreamConsumer():
    def __init__(self, settings:ConsumerSettings, client:IRedisClient, consumer:IMessageConsumer) -> None:
        self._settings:ConsumerSettings = settings
        self._client:IRedisClient = client
        self._consumer:IMessageConsumer = consumer


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
            connection.xgroup_create(name=self._settings.stream_name, groupname=self._settings.group_name, id="0", mkstream=True)
            print(f"Created consumer group '{self._settings.group_name}' on stream '{self._settings.stream_name}'")
        except redis.ResponseError as e:
            if "BUSYGROUP" in str(e):
                print(f"Consumer group '{self._settings.group_name}' already exists.")
            else:
                raise


    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def process_message(self, msg_id:str, msg_data:Dict[str, Any]) -> None:
        print(f"Processing message {msg_id}: {str(msg_data)}")
        # args:MessageArgs = MessageArgs(
        #     data=msg_data.get("data", ""),
        #     correlation_id=msg_data.get("correlationId", ""),
        #     service_name=msg_data.get("serviceName", ""),
        #     server_name=msg_data.get("serverName", ""),
        #     send_at=msg_data.get("sendAt", None),
        # )

        await self._consumer.on_consume(
            correlation_id=msg_data.get("correlationId", ""),
            json64=msg_data.get("data", ""),
            service_name=msg_data.get("serviceName", ""))


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
        results = connection.xreadgroup(
            groupname=self._settings.group_name,
            consumername=self._settings.consumer_name,
            streams={self._settings.stream_name: '>'},
            count=10,
            block=5000
        )

        if results:
            for stream, messages in results:
                for msg_id, msg_data in messages:
                    try:
                        await self.process_message(msg_id, msg_data)
                        self._ack_message(connection, msg_id)
                    except Exception as e:
                        print(f"Failed to process message {msg_id}: {e}")
                        
                        # Write to dead letter stream
                        connection.xadd(
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
                        self._ack_message(connection, msg_id)
        else:
            # If no messages were processed, check for pending messages to claim
            await self._claim_pending(connection)


    def _ack_message(self, connection:C, msg_id:str) -> None:
        """ Acknowledge a message in the stream. """
        connection.xack(self._settings.stream_name, self._settings.group_name, msg_id)
        if (self._settings.deleteAfterAck):
            connection.xdel(self._settings.stream_name, msg_id)


    async def _claim_pending(self, connection:C) -> None:
        """ Claim pending messages from failed consumers older than X seconds. """
        pending = connection.xpending_range(self._settings.stream_name, self._settings.group_name, min="-", max="+", count=10)
        for p in pending:
            message_id, consumer, elapsed_ms, delivery_count = p
            claim_after_ms:int = self._settings.claim_after_seconds * 1000
            if elapsed_ms > claim_after_ms:
                print(f"Claiming message {message_id} from {consumer}")
                claimed = connection.xclaim(
                    name=self._settings.stream_name,
                    groupname=self._settings.group_name,
                    consumername=self._settings.consumer_name,
                    min_idle_time=claim_after_ms,
                    message_ids=[message_id],
                )

                for mid, data in claimed:
                    await self.process_message(mid, data)
                    connection.xack(self._settings.stream_name, self._settings.group_name, mid)
