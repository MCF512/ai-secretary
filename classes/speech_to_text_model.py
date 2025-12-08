from pathlib import Path
from typing import Any, Union

import librosa
import numpy as np
from transformers import pipeline

from .ml_model import MLModel


ArrayLike = Union[np.ndarray, list[float]]


class SpeechToTextModel(MLModel):
    def __init__(
        self,
        model_path: str = "bond005/whisper-podlodka-turbo",
        language: str = "ru",
        target_sampling_rate: int = 16_000,
    ):
        super().__init__(model_path, "speech_to_text")
        self._language: str = language
        self._accuracy: float = 0.0
        self._target_sr: int = target_sampling_rate

    def load_model(self) -> None:
        self._model = pipeline(
            model=self._model_path,
            device="cpu",
        )
        self._is_loaded = True

    def predict(self, audio: Union[str, Path, ArrayLike]) -> str:
        if not self._is_loaded:
            self.load_model()

        audio_array = self._to_mono_array(audio)

        result = self._model(
            audio_array,
            generate_kwargs={"task": "transcribe", "language": self._language},
            return_timestamps=False,
        )
        text = result["text"]

        if isinstance(text, str):
            text = text.strip()
        return text

    def save_model(self, path: str) -> None:
        pass

    def set_language(self, language: str) -> None:
        self._language = language

    def get_accuracy(self) -> float:
        return self._accuracy

    def _to_mono_array(self, audio: Union[str, Path, ArrayLike]) -> np.ndarray:
        if isinstance(audio, (str, Path)):
            path = str(audio)
            y, _ = librosa.load(path, sr=self._target_sr, mono=True)
            return y

        if isinstance(audio, list):
            audio = np.asarray(audio, dtype=np.float32)

        if isinstance(audio, np.ndarray):
            if audio.ndim == 1:
                return librosa.resample(audio, orig_sr=self._target_sr, target_sr=self._target_sr)
            if audio.ndim == 2:
                mono = librosa.to_mono(audio)
                return librosa.resample(mono, orig_sr=self._target_sr, target_sr=self._target_sr)

        raise TypeError("audio must be path to file, list or numpy array")
