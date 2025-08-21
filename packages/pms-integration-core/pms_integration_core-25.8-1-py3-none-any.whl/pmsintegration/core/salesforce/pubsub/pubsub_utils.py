import io
import logging
import threading
from collections.abc import Callable
from typing import Generator

import avro.io
import avro.schema

from pmsintegration.core.salesforce.pubsub import types
from pmsintegration.core.salesforce.store import SubscribeParams
from pmsintegration.platform import errors
from pmsintegration.platform.concurrent_utils import halt_requested

_log = logging.getLogger(__name__)


class LockMechanism:
    def __init__(self):
        self.semaphore = threading.Semaphore(1)
        self.is_done = False


class Subscription:
    def __init__(self, event_stream, callback):
        self.event_stream = event_stream
        self.callback = callback

    def run_forever(self):
        for event in self.event_stream:
            is_done = self.callback(event)
            if is_done:
                _log.info("***** Subscription was requested to stop by the callback")
                break
            if halt_requested():
                _log.info("***** Subscription is going to to stopped by the process halt")
                break


def decode_avro_payload(schema, payload):
    """
    Uses Avro and the event schema to decode a serialized payload. The
    `encode()` and `decode()` methods are helper functions to serialize and
    deserialize the payloads of events that clients will publish and
    receive using Avro. If you develop an implementation with a language
    other than Python, you will need to find an Avro library in that
    language that helps you encode and decode with Avro. When publishing an
    event, the plaintext payload needs to be Avro-encoded with the event
    schema for the API to accept it. When receiving an event, the
    Avro-encoded payload needs to be Avro-decoded with the event schema for
    you to read it in plaintext.
    """
    schema = avro.schema.parse(schema)
    buf = io.BytesIO(payload)
    decoder = avro.io.BinaryDecoder(buf)
    reader = avro.io.DatumReader(schema)
    ret = reader.read(decoder)
    return ret


def fetch_req_stream(
        lock_mechanism: LockMechanism,
        topic: str,
        subscription_params_provider: Callable[[], SubscribeParams],
        num_requested: int
) -> Generator[types.FetchRequest, None, None]:
    """Returns a FetchRequest stream for the Subscribe RPC.

    """
    while True:
        lock_mechanism.semaphore.acquire()
        if lock_mechanism.is_done:
            _log.info(f"Fetch stream request generator was being ask to stop for topic: {topic} ")
            break
        p = subscription_params_provider()
        replay_type = p.replay_type
        replay_id = p.replay_id

        replay_preset = {
            "LATEST": types.ReplayPreset.LATEST,
            "EARLIEST": types.ReplayPreset.EARLIEST,
            "CUSTOM": types.ReplayPreset.CUSTOM,
        }.get(replay_type)

        if replay_preset is None:
            raise errors.IllegalArgumentException(f"Invalid Replay Type '{replay_type}'")

        _log.info(
            f"Sending Fetch Request ({num_requested}) "
            f"for topic: {topic} using replay_id: {replay_id} ({replay_type})"
        )

        yield types.FetchRequest(
            topic_name=topic,
            replay_preset=replay_preset,
            replay_id=bytes.fromhex(replay_id),
            num_requested=num_requested
        )
