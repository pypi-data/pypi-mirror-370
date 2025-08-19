from pydub import AudioSegment

from Models.talk_metadata import TalkMetadata


class AudioChunkInfo:
    def __init__(self, arr_fltp, arr_int16, duration, samples_count, sample_rate):
        self._samples_fltp = arr_fltp
        self._samples_int16 = arr_int16
        self._duration = duration
        self._samples_count = samples_count
        self._sample_rate = sample_rate

    @property
    def samples_fltp(self):
        return self._samples_fltp

    @property
    def samples_int16(self):
        return self._samples_int16

    @property
    def duration(self):
        return self._duration

    @property
    def samples_count(self):
        return self._samples_count

    @property
    def sample_rate(self):
        return self._sample_rate


class AudioData:
    def __init__(
        self,
        samples,
        mel_chunks,
        duration,
        samples_count,
        sample_rate,
        metadata: TalkMetadata,
    ):
        self._samples = samples
        self._mel_chunks = mel_chunks
        self._duration = duration
        self._samples_count = samples_count
        self._sample_rate = sample_rate
        self._metadata = metadata

    @property
    def samples(self):
        return self._samples

    @property
    def mel_chunks(self):
        return self._mel_chunks

    @property
    def duration(self):
        return self._duration

    @property
    def metadata(self):
        return self._metadata

    @property
    def samples_count(self):
        return self._samples_count

    @property
    def sample_rate(self):
        return self._sample_rate
