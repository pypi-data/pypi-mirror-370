from enum import Enum


class LLMProvider(Enum):
    OPENAI = "openai"
    GEMINI = "gemini"


class Configuration:
    def __init__(
        self,
        input_type: str = "mic",
        default_voice: str = "nova",
        llm_provider: LLMProvider = LLMProvider.OPENAI,
        stt_model: str = "nova-3",
        stt_prompt: str = "",
        stt_endpointing: int = 300,
        stt_language: str = "en",
        module_rule: str = "default",
        recording_enabled: bool = False,
        timeout: int = 5,
        audio_input_delay: int = 0,
    ):
        self.input_type = input_type
        self.default_voice = default_voice
        self.stt_model = stt_model
        self.stt_prompt = stt_prompt
        self.stt_endpointing = stt_endpointing
        self.stt_language = stt_language
        self.module_rule = module_rule
        self.recording_enabled = recording_enabled
        self.timeout = timeout
        self.audio_input_delay = audio_input_delay

        if isinstance(llm_provider, str):
            self.llm_provider = LLMProvider(llm_provider)
        else:
            self.llm_provider = llm_provider

    def set_llm_provider(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    def __dict__(self):
        return {
            "input_type": self.input_type,
            "default_voice": self.default_voice,
            "llm_provider": self.llm_provider.value,
            "stt_model": self.stt_model,
            "stt_prompt": self.stt_prompt,
            "stt_endpointing": self.stt_endpointing,
            "stt_language": self.stt_language,
            "module_rule": self.module_rule,
            "recording_enabled": self.recording_enabled,
            "timeout": self.timeout,
            "audio_input_delay": self.audio_input_delay,
        }
