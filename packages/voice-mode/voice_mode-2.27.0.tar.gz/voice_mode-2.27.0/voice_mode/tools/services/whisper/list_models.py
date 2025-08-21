"""MCP tool for listing Whisper models and their status."""

from typing import Dict, Any
from voice_mode.tools.services.whisper.models import (
    WHISPER_MODELS,
    get_model_directory,
    get_current_model,
    is_model_installed,
    get_installed_models,
    format_size,
    has_coreml_model,
    is_apple_silicon
)


async def list_whisper_models() -> Dict[str, Any]:
    """List available Whisper models and their installation status.
    
    Returns:
        Dictionary containing model information and status
    """
    try:
        model_dir = get_model_directory()
        current_model = get_current_model()
        installed_models = get_installed_models()
        
        # Build models list with status
        models = []
        show_coreml = is_apple_silicon()  # Only show Core ML on Apple Silicon
        
        for model_name, info in WHISPER_MODELS.items():
            model_status = {
                "name": model_name,
                "size_mb": info["size_mb"],
                "size": format_size(info["size_mb"]),
                "languages": info["languages"],
                "description": info["description"],
                "installed": is_model_installed(model_name),
                "current": model_name == current_model,
                "has_coreml": has_coreml_model(model_name) if show_coreml else False
            }
            models.append(model_status)
        
        # Calculate totals
        total_installed_size = sum(
            WHISPER_MODELS[m]["size_mb"] for m in installed_models
        )
        total_available_size = sum(
            m["size_mb"] for m in WHISPER_MODELS.values()
        )
        
        return {
            "success": True,
            "models": models,
            "current_model": current_model,
            "model_directory": str(model_dir),
            "installed_count": len(installed_models),
            "total_count": len(WHISPER_MODELS),
            "installed_size_mb": total_installed_size,
            "installed_size": format_size(total_installed_size),
            "available_size_mb": total_available_size,
            "available_size": format_size(total_available_size)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "models": []
        }