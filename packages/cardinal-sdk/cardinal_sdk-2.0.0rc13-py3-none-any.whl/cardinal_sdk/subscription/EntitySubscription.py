from typing import Generic, TypeVar, List, Optional, Callable
from ctypes import c_void_p, cast, c_char_p
from concurrent.futures import Executor

from cardinal_sdk.async_utils import execute_async_method_job
from cardinal_sdk.kotlin_types import symbols, DATA_RESULT_CALLBACK_FUNC
from cardinal_sdk.model import EntitySubscriptionCloseReason
from cardinal_sdk.model.CallResult import create_result_from_json
from datetime import timedelta
from cardinal_sdk.subscription.EntitySubscriptionEvent import EntitySubscriptionEvent
import math
import asyncio
import json


T = TypeVar('T')


class EntitySubscription(Generic[T]):
    def __init__(self, producer: c_void_p, deserializer: Callable[[object], T], executor: Optional[Executor] = None):
        self.__producer = producer
        self.__deserializer = deserializer
        self.__executor = executor

    def __del__(self):
        symbols.kotlin.root.com.icure.cardinal.sdk.py.utils.disposeStablePtr(self.__producer)

    """
    Closes the subscription, no new event will be created.
    Note: you should always close a subscription when not using it anymore, in order to properly release the associated
    resources.
    """
    def close(self):
        call_result = symbols.kotlin.root.com.icure.cardinal.sdk.py.subscription.EntitySubscription.close(self.__producer)
        result_info = create_result_from_json(cast(call_result, c_char_p).value.decode('utf-8'))
        symbols.DisposeString(call_result)
        if result_info.failure is not None:
            raise Exception(result_info.failure)

    """
    Returns the reason why the subscription is closed, or None if the subscription is not yet closed.
    """
    def get_close_reason(self) -> Optional[EntitySubscriptionCloseReason]:
        call_result = symbols.kotlin.root.com.icure.cardinal.sdk.py.subscription.EntitySubscription.getCloseReason(self.__producer)
        result_info = create_result_from_json(cast(call_result, c_char_p).value.decode('utf-8'))
        symbols.DisposeString(call_result)
        if result_info.failure is not None:
            raise Exception(result_info.failure)
        elif result_info.success is not None:
            return EntitySubscriptionCloseReason._deserialize(result_info.success)
        else:
            return None

    """
    Consume the next event in the subscription event queue or None if there is currently no event. If the subscription is
    closed you can still retrieved any unconsumed event, but no new event will be added to the queue.
    """
    def get_event(self) -> Optional[EntitySubscriptionEvent[T]]:
        call_result = symbols.kotlin.root.com.icure.cardinal.sdk.py.subscription.EntitySubscription.getEvent(self.__producer)
        result_info = create_result_from_json(cast(call_result, c_char_p).value.decode('utf-8'))
        symbols.DisposeString(call_result)
        if result_info.failure is not None:
            raise Exception(result_info.failure)
        else:
            return self.__decode_event(result_info.success)

    """
    Waits for the next event in the subscription event queue and consumes it, or return None if no new event is produced
    within the provided timeout.
    """
    def wait_for_event_blocking(self, timeout: timedelta) -> Optional[EntitySubscriptionEvent[T]]:
        call_result = symbols.kotlin.root.com.icure.cardinal.sdk.py.subscription.EntitySubscription.waitForEventBlocking(
            self.__producer,
            EntitySubscription.__time_delta_ms(timeout)
        )
        result_info = create_result_from_json(cast(call_result, c_char_p).value.decode('utf-8'))
        symbols.DisposeString(call_result)
        if result_info.failure is not None:
            raise Exception(result_info.failure)
        else:
            return self.__decode_event(result_info.success)

    """
    Waits for the next event in the subscription event queue and consumes it, or return None if no new event is produced
    within the provided timeout.
    """
    async def wait_for_event_async(self, timeout: timedelta) -> Optional[EntitySubscriptionEvent[T]]:
        return await execute_async_method_job(
            self.__executor,
            True,
            self.__decode_event,
            symbols.kotlin.root.com.icure.cardinal.sdk.py.subscription.EntitySubscription.waitForEventAsync,
            self.__producer,
            EntitySubscription.__time_delta_ms(timeout),
        )

    def __decode_event(self, encoded_event) -> Optional[EntitySubscriptionEvent[T]]:
        if encoded_event is not None:
            return EntitySubscriptionEvent.deserialize_entity_subscription_event(encoded_event, self.__deserializer)
        else:
            return None

    @staticmethod
    def __time_delta_ms(delta: timedelta) -> int:
        total_milliseconds = delta.total_seconds() * 1000
        return math.ceil(total_milliseconds)
