#!/usr/bin/env python3

"""Check that the asynchrone decoding of the audio and video files goes well."""

from fractions import Fraction
import math
import queue
import threading

import torch

from cutcutcodec.core.io.read_ffmpeg import ContainerInputFFMPEG


def test_async_audio():
    """Read audio async."""
    res_queue = queue.Queue()
    lock = threading.Lock()

    def _snapshot_put(ind, stream, timestamp, rate, samples):
        frame = stream.snapshot(timestamp, rate, samples)
        with lock:
            res_queue.put((ind, frame))

    with ContainerInputFFMPEG("cutcutcodec/examples/audio_5.1_narration.oga") as container:
        (stream,) = container.out_streams
        frames = [
            stream.snapshot(Fraction(i, stream.rate), stream.rate, 512)
            for i in range(0, math.ceil(stream.duration * stream.rate)-513, 512)
        ]

        tasks = [
            threading.Thread(
                target=_snapshot_put, args=(i, stream, f.time, stream.rate, 512), daemon=True
            )
            for i, f in enumerate(frames)
        ]
        for task in tasks:
            task.start()
        for task in tasks:
            task.join()
    for _ in range(len(frames)):
        ind, frame = res_queue.get_nowait()
        assert frames[ind].time == frame.time
        assert torch.equal(frame, frames[ind]), (frame, frames[ind])


def test_async_video():
    """Read video async."""
    res_queue = queue.Queue()
    lock = threading.Lock()

    def _snapshot_put(ind, stream, timestamp, shape):
        frame = stream.snapshot(timestamp, shape)
        with lock:
            res_queue.put((ind, frame))

    with ContainerInputFFMPEG("cutcutcodec/examples/video.mp4") as container:
        (stream,) = container.out_streams
        shape = (stream.height, stream.width)
        frames = [
            stream.snapshot(i/stream.rate, shape)
            for i in range(math.ceil(stream.duration*stream.rate))
        ]

        tasks = [
            threading.Thread(target=_snapshot_put, args=(i, stream, f.time, shape), daemon=True)
            for i, f in enumerate(frames)
        ]
        for task in tasks:
            task.start()
        for task in tasks:
            task.join()
    for _ in range(len(frames)):
        ind, frame = res_queue.get_nowait()
        assert frames[ind].time == frame.time
        assert torch.equal(frame, frames[ind]), (frame, frames[ind])
