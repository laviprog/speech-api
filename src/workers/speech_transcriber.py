import gc

import torch
from numpy import ndarray
from whisperx.alignment import align, load_align_model
from whisperx.asr import FasterWhisperPipeline, load_model
from whisperx.audio import load_audio
from whisperx.diarize import DiarizationPipeline, assign_word_speakers
from whisperx.schema import AlignedTranscriptionResult, SingleSegment, TranscriptionResult

from src.transcription.enums import Language, Model
from src.workers import log


class SpeechTranscriber:
    """
    Handles speech transcription, alignment, and speaker diarization using WhisperX.
    """

    def __init__(
        self,
        device: str,
        compute_type: str,
        download_root: str,
        batch_size: int,
        chunk_size: int,
        init_models: list[Model] | None = None,
        hf_token: str | None = None,
    ):
        """
        Initializes the SpeechTranscription with device configuration
        and optional models to preload.

        :param device: Device to use for inference ("cpu" or "cuda").
        :param compute_type: Compute type for inference (e.g., "float32", "int8").
        :param download_root: Directory for downloading and caching models.
        :param init_models: Optional list of models to preload at startup.
        :param batch_size: Batch size for inference.
        :param chunk_size: Chunk size (in seconds) for audio splitting.
        :param hf_token: Optional Hugging Face token for private diarization model access.
        """
        self.__asr_cache: dict[str, FasterWhisperPipeline] = {}
        self.__align_cache: dict[str, tuple] = {}
        self.__diar_cache: DiarizationPipeline | None = None

        self._device = device
        self._compute_type = compute_type
        self._download_root = download_root
        self._batch_size = batch_size
        self._chunk_size = chunk_size
        self._hf_token = hf_token

        self._load_models(init_models)

    def _load_models(self, models: list[Model] | None) -> None:
        """
        Preloads specified ASR models into cache.
        """
        if not models:
            return
        for model in models:
            self._load_asr(model.value)

    def _get_asr(self, model: Model) -> FasterWhisperPipeline:
        """
        Retrieves the ASR model from cache or loads it if not present.
        """
        key = model.value
        if key not in self.__asr_cache:
            self._load_asr(key)
        return self.__asr_cache[key]

    def _load_asr(self, model_name: str) -> None:
        """
        Loads an ASR model and stores it in the cache.
        """
        log.debug("Loading ASR model", model_name=model_name)
        try:
            self.__asr_cache[model_name] = load_model(
                whisper_arch=model_name,
                device=self._device,
                compute_type=self._compute_type,
                download_root=self._download_root,
            )
            log.debug("Loaded ASR model", model_name=model_name)
        except Exception as e:
            log.error("Failed to load ASR model", model_name=model_name, error=str(e))
            raise e

    def _get_align(self, lang_code: str):
        """
        Retrieves the alignment model for the specified language code from cache or loads it
        if not present.
        """
        if lang_code not in self.__align_cache:
            log.debug("Loading align model", lang_code=lang_code)
            try:
                align_model, metadata = load_align_model(
                    language_code=lang_code,
                    device=self._device,
                    model_dir=self._download_root,
                )
                self.__align_cache[lang_code] = (align_model, metadata)
                log.debug("Align model loaded", lang_code=lang_code)
            except Exception as e:
                log.error("Failed to load align model", lang_code=lang_code, error=str(e))
                raise
        return self.__align_cache[lang_code]

    def _get_diar(self) -> DiarizationPipeline:
        """
        Retrieves the diarization model from cache or loads it if not present.
        """
        if self.__diar_cache is None:
            if not self._hf_token:
                raise RuntimeError("HuggingFace token is required for diarization")
            log.debug("Loading diarization pipeline...")
            try:
                self.__diar_cache = DiarizationPipeline(
                    use_auth_token=self._hf_token,
                    device=self._device,
                )
                log.debug("Diarization pipeline loaded")
            except Exception as e:
                log.error("Failed to load diarization pipeline", error=str(e))
                raise
        return self.__diar_cache

    @staticmethod
    def _load_audio(audio_file: str) -> ndarray:
        """
        Loads audio file into a numpy array.
        """
        log.debug("Loading audio file", audio_file=audio_file)
        try:
            audio = load_audio(file=audio_file)
            log.debug("Loaded audio file", audio_file=audio_file)
        except RuntimeError as e:
            log.error("Failed to load audio file", audio_file=audio_file, error=str(e))
            raise e
        return audio

    def _transcribe(
        self,
        audio: ndarray,
        audio_file: str,
        model: Model,
        language: Language,
    ) -> TranscriptionResult:
        """
        Transcribes the given audio using the specified ASR model and language.
        """
        asr = self._get_asr(model)

        log.debug(
            "Transcribing...",
            model=str(model),
            language=str(language),
            batch_size=self._batch_size,
            chuck_size=self._chunk_size,
        )
        try:
            result = asr.transcribe(
                audio=audio,
                language=str(language),
                batch_size=self._batch_size,
                chunk_size=self._chunk_size,
            )
            log.debug("Transcribed audio file %s", audio_file)
        except Exception as e:
            log.error("Transcribing failed", audio_file=audio_file, error=str(e))
            raise e

        return result

    def _align(
        self, segments: list[SingleSegment], audio: ndarray, language: Language
    ) -> AlignedTranscriptionResult | None:
        """
        Aligns the transcription segments with the audio using the alignment model.
        """
        try:
            align_model, metadata = self._get_align(language)
            return align(
                segments,
                align_model,
                metadata,
                audio,
                device=self._device,
            )
        except Exception as e:
            log.warning("Alignment failed (fallback to raw segments)", error=str(e))
            return None

    def _diarize(
        self, transcription_result: TranscriptionResult, audio: ndarray, num_speakers: int
    ) -> TranscriptionResult:
        """
        Performs speaker diarization and assigns speakers to transcription segments.
        """
        diarization_model = self._get_diar()
        log.debug(
            "Running diarization",
            num_speakers=num_speakers,
        )
        try:
            diar_segments = diarization_model(audio, num_speakers=num_speakers)
            return assign_word_speakers(diar_segments, transcription_result)
        except Exception as e:
            log.error("Diarization failed", error=str(e))
            return transcription_result

    def transcribe(
        self,
        audio_file: str,
        model: Model,
        language: Language,
        recognition_mode: bool,
        num_speakers: int | None,
    ) -> list[SingleSegment]:
        """
        Transcribes the given audio file, optionally performing speaker diarization.
        """
        audio = self._load_audio(audio_file)

        transcription_result = self._transcribe(
            audio=audio,
            audio_file=audio_file,
            model=model,
            language=language,
        )

        align_result = self._align(
            segments=transcription_result["segments"],
            audio=audio,
            language=language,
        )

        if align_result:
            transcription_result["segments"] = [
                SingleSegment(start=seg["start"], end=seg["end"], text=seg["text"].strip())
                for seg in align_result["segments"]
            ]

        if recognition_mode:
            transcription_result = self._diarize(transcription_result, audio, num_speakers)

        return transcription_result["segments"]

    def clean(self) -> None:
        """
        Cleans up cached models and frees memory.
        """
        log.debug("Cleaning up resources...")
        self.__asr_cache.clear()
        self.__align_cache.clear()
        self.__diar_cache = None
        gc.collect()
        if self._device.startswith("cuda") and torch.cuda.is_available():
            torch.cuda.empty_cache()
        log.debug("Cleanup complete")
