import os
import logging
from pathlib import Path
from typing import Optional, Callable
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class VeoClient:
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in .env file")
            self._client = genai.Client(api_key=api_key)
    
    @property
    def client(self):
        return self._client

class StorageManager:
    def __init__(self, base_path: Optional[str] = None):
        """Manage output directories for videos, frames, and temp files.

        Default resolution order for base path:
        1. VEO_OUTPUT_DIR environment variable (if set)
        2. Current working directory (./output)
        3. Package-adjacent directory (../output) as a last resort
        """
        resolved_base: Path

        # 1) Environment override
        env_base = os.getenv("VEO_OUTPUT_DIR")
        if base_path:
            resolved_base = Path(base_path)
        elif env_base:
            resolved_base = Path(env_base)
        else:
            # 2) Prefer CWD/output for installed packages (CLI/scripts)
            cwd_candidate = Path.cwd() / "output"
            try:
                cwd_candidate.mkdir(parents=True, exist_ok=True)
                resolved_base = cwd_candidate
            except Exception:
                # 3) As a last resort, place beside the installed package
                try:
                    package_root = Path(__file__).resolve().parents[2]
                    candidate = package_root / "output"
                    candidate.mkdir(parents=True, exist_ok=True)
                    resolved_base = candidate
                except Exception:
                    # Final fallback: user home
                    resolved_base = Path.home() / "output"

        self.base_path = resolved_base
        self.base_path.mkdir(parents=True, exist_ok=True)

        self.videos_dir = self.base_path / "videos"
        self.frames_dir = self.base_path / "frames"
        self.temp_dir = self.base_path / "temp"

        for dir_path in [self.videos_dir, self.frames_dir, self.temp_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def get_video_path(self, filename: str) -> Path:
        return self.videos_dir / filename
    
    def get_frame_path(self, filename: str) -> Path:
        return self.frames_dir / filename
    
    def get_temp_path(self, filename: str) -> Path:
        return self.temp_dir / filename
    
    def cleanup_temp(self):
        for file in self.temp_dir.glob("*"):
            try:
                file.unlink()
            except:
                pass
    
    def get_url(self, path: Path) -> Optional[str]:
        if path.exists():
            return f"file://{path.absolute()}"
        return None

class ProgressTracker:
    def __init__(self, callback: Optional[Callable] = None):
        self.callback = callback or self.default_progress
        self.current_progress = 0
        self.logger = logging.getLogger(__name__)
    
    def default_progress(self, message: str, percent: int):
        self.logger.info(f"{message}: {percent}%")
    
    def update(self, message: str, percent: int):
        self.current_progress = percent
        self.callback(message, percent)
    
    def start(self, message: str = "Starting"):
        self.update(message, 0)
    
    def complete(self, message: str = "Complete"):
        self.update(message, 100)

class ModelConfig:
    MODELS = {
        "veo-3.0-fast-generate-preview": {
            "name": "Veo 3.0 Fast",
            "supports_duration": False,
            "supports_enhance": False,
            "supports_fps": False,
            "supports_aspect_ratio": True,
            "supports_audio": True,
            "default_duration": 8,
            "generation_time": 60
        },
        "veo-3.0-generate-preview": {
            "name": "Veo 3.0",
            "supports_duration": False,
            "supports_enhance": False,
            "supports_fps": False,
            "supports_aspect_ratio": True,
            "supports_audio": True,
            "default_duration": 8,
            "generation_time": 120
        },
        "veo-2.0-generate-001": {
            "name": "Veo 2.0",
            "supports_duration": True,
            "supports_enhance": True,
            "supports_fps": True,
            "supports_aspect_ratio": True,
            "supports_audio": False,
            "default_duration": 5,
            "generation_time": 180
        }
    }
    
    @classmethod
    def get_config(cls, model: str) -> dict:
        if model.startswith("models/"):
            model = model.replace("models/", "")
        
        return cls.MODELS.get(model, cls.MODELS["veo-3.0-fast-generate-preview"])
    
    @classmethod
    def build_generation_config(cls, model: str, **kwargs) -> types.GenerateVideosConfig:
        config = cls.get_config(model)
        
        params = {
            "number_of_videos": kwargs.get("number_of_videos", 1)
        }
        
        if config["supports_duration"] and "duration_seconds" in kwargs:
            params["duration_seconds"] = kwargs["duration_seconds"]
        
        if config["supports_enhance"]:
            params["enhance_prompt"] = kwargs.get("enhance_prompt", False)
        
        if config["supports_fps"] and "fps" in kwargs:
            params["fps"] = kwargs["fps"]

        # Aspect ratio (e.g., "16:9"; Veo 3 limited to 16:9; Veo 2 supports 16:9 and 9:16)
        if config.get("supports_aspect_ratio") and "aspect_ratio" in kwargs and kwargs["aspect_ratio"]:
            ar = str(kwargs["aspect_ratio"])  # normalize
            model_key = model.replace("models/", "")
            if model_key.startswith("veo-3.0"):
                allowed = {"16:9"}
            elif model_key.startswith("veo-2.0"):
                allowed = {"16:9", "9:16"}
            else:
                allowed = {"16:9"}
            if ar not in allowed:
                raise ValueError(f"aspect_ratio '{ar}' not supported for model '{model_key}'. Allowed: {sorted(allowed)}")
            params["aspect_ratio"] = ar

        # Docs-backed pass-throughs
        if "negative_prompt" in kwargs and kwargs["negative_prompt"]:
            params["negative_prompt"] = kwargs["negative_prompt"]

        if "person_generation" in kwargs and kwargs["person_generation"]:
            # Person generation options vary by model/region; pass through as provided
            params["person_generation"] = kwargs["person_generation"]
        
        # Safety settings (optional, SDK >= 1.30.0 for some modalities). Accept either
        # a list of dicts {category, threshold} or already-constructed types.SafetySetting.
        safety_settings = kwargs.get("safety_settings")
        if safety_settings:
            normalized: list = []
            for item in safety_settings:
                try:
                    if hasattr(item, "category") and hasattr(item, "threshold"):
                        normalized.append(item)
                    elif isinstance(item, dict):
                        normalized.append(types.SafetySetting(
                            category=item.get("category"),
                            threshold=item.get("threshold"),
                        ))
                except Exception:
                    # Ignore malformed entries
                    continue
            if normalized:
                params["safety_settings"] = normalized

        # Cached content handle (best-effort pass-through if supported)
        if "cached_content" in kwargs and kwargs["cached_content"]:
            params["cached_content"] = kwargs["cached_content"]
        
        # Construct config, dropping unknown fields if the SDK doesn't support them
        try:
            return types.GenerateVideosConfig(**params)
        except TypeError:
            # Remove optional fields that may not be recognized by this client version
            for optional_key in ["safety_settings", "cached_content"]:
                params.pop(optional_key, None)
            return types.GenerateVideosConfig(**params)