from typing import Optional
import numpy as np
from loguru import logger
from pipecat.audio.filters.base_audio_filter import BaseAudioFilter
from pipecat.frames.frames import FilterControlFrame, FilterEnableFrame
from pipecat.audio.utils import create_default_resampler
import time


try:
    from pyrnnoise import RNNoise
except ModuleNotFoundError as e:
    logger.error(f"Exception: {e}")
    logger.error(
        "In order to use the PyRnnNoise filter, add `pyrnnoise` to remote-requirements.txt/requirements.txt."
    )
    raise Exception(f"Missing module: {e}")


# Sadly BaseAudioFilter has no concept of tracking metrics.
class PyRnnNoiseLocalFilter(BaseAudioFilter):
    """Audio filter that uses PyRNNoise."""

    def __init__(self) -> None:
        self._filtering = True
        self._sample_rate = 0
        self._filter_ready = True
        self.denoiser: Optional[RNNoise] = None
        self.resampler = create_default_resampler()
        self.model_sample_rate = 48000

        self._frame_size = 480  # py rnn needs the frame size to be 480
        self._resampled_buffer = np.empty(0, dtype=np.int16)
        self.metric_tracker = list()  # will see how i can export this

    async def start(self, sample_rate: int):
        self._sample_rate = sample_rate
        self.denoiser = RNNoise(self.model_sample_rate)
        self.denoiser.channels = 1
        self._resampled_buffer = np.empty(0, dtype=np.int16)

    async def stop(self):
        # nothing to reset
        pass

    async def process_frame(self, frame: FilterControlFrame):
        if isinstance(frame, FilterEnableFrame):
            self._filtering = frame.enable

    async def filter(self, audio: bytes) -> bytes:
        if not self._filtering or not audio:
            return audio

        s_time = time.perf_counter()
        resampled_audio_bytes = await self.resampler.resample(
            audio, self._sample_rate, self.model_sample_rate
        )

        incoming = np.frombuffer(resampled_audio_bytes, dtype=np.int16)
        if self._resampled_buffer.size:
            data = np.concatenate([self._resampled_buffer, incoming])
        else:
            data = incoming

        out_frames = []
        pos = 0
        n = data.shape[0]

        # pipecat sends 160 samples in a frame at a sampling rate of 8000 which is 20 ms of audio data. Pyrnn needs 10 ms of data in a frame at 48000 sampling rate
        while pos + self._frame_size <= n:
            frame = data[pos : pos + self._frame_size]

            frame_2d = np.atleast_2d(frame)
            _, denoised = self.denoiser.denoise_frame(frame_2d, partial=False)
            out_frames.append(denoised[0])
            pos += self._frame_size

        # TODO: In @UT in some cases small amount of audio gets left inside this (2-3 ms), need to send that back as it is.
        self._resampled_buffer = data[pos:]

        if not out_frames:
            return b""

        cleaned_audio = np.concatenate(out_frames)
        filtered_audio_bytes = (
            np.clip(cleaned_audio, -32768, 32767).astype(np.int16, copy=False).tobytes()
        )
        resampled_filtered_audio_bytes = await self.resampler.resample(
            filtered_audio_bytes, self.model_sample_rate, self._sample_rate
        )
        """
        logger.debug( 
            len(incoming),
            len(cleaned_audio),
            len(self._resampled_buffer),
            self._sample_rate,
            self.model_sample_rate,
        )"""
        # self.metric_tracker.append(time.perf_counter() - s_time)
        return resampled_filtered_audio_bytes
