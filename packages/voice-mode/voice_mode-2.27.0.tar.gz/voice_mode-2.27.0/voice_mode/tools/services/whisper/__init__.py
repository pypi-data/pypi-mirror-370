"""Whisper service tools."""

from voice_mode.tools.services.whisper.install import whisper_install
from voice_mode.tools.services.whisper.uninstall import whisper_uninstall
from voice_mode.tools.services.whisper.download_model import download_model
from voice_mode.tools.services.whisper.list_models_tool import whisper_list_models

__all__ = [
    'whisper_install',
    'whisper_uninstall', 
    'download_model',
    'whisper_list_models'
]