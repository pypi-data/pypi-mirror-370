"""Download Whisper models with Core ML support."""

import os
import json
import logging
from pathlib import Path
from typing import Union, List

from voice_mode.server import mcp
from voice_mode.config import logger, MODELS_DIR
from voice_mode.utils.services.whisper_helpers import download_whisper_model, get_available_models

logger = logging.getLogger("voice-mode")


@mcp.tool()
async def download_model(
    model: Union[str, List[str]] = "large-v2",
    force_download: Union[bool, str] = False,
    skip_core_ml: Union[bool, str] = False
) -> str:
    """Download Whisper model(s) with optional Core ML conversion.
    
    Downloads whisper.cpp models to the configured directory. On Apple Silicon,
    automatically converts models to Core ML format for better performance.
    
    Args:
        model: Model name(s) to download. Can be:
               - Single model: "large-v2"
               - List of models: ["base", "small"]
               - "all" to download all available models
        force_download: Re-download even if model exists (default: False)
        skip_core_ml: Skip Core ML conversion on Apple Silicon (default: False)
        
    Available models:
        - tiny, tiny.en
        - base, base.en
        - small, small.en
        - medium, medium.en
        - large-v1, large-v2, large-v3
        - large-v3-turbo
        
    Returns:
        Status message with download results
        
    Examples:
        # Download default model
        download_model()
        
        # Download specific model
        download_model("small.en")
        
        # Download multiple models
        download_model(["base", "small", "medium"])
        
        # Download all models
        download_model("all")
        
        # Force re-download
        download_model("large-v3", force_download=True)
    """
    try:
        # Get model directory from configuration
        models_dir = MODELS_DIR / "whisper"
        
        # Check both possible whisper installation locations
        whisper_install_dir = Path.home() / ".voicemode" / "services" / "whisper"
        legacy_install_dir = Path.home() / ".voicemode" / "whisper.cpp"
        
        if whisper_install_dir.exists():
            actual_models_dir = whisper_install_dir / "models"
        elif legacy_install_dir.exists():
            actual_models_dir = legacy_install_dir / "models"
        else:
            return json.dumps({
                "success": False,
                "error": "Whisper.cpp not installed. Please run whisper_install first."
            }, indent=2)
        
        # Parse model input
        available_models = get_available_models()
        
        if isinstance(model, str):
            if model.lower() == "all":
                models_to_download = available_models
            else:
                models_to_download = [model]
        else:
            models_to_download = model
        
        # Validate models
        invalid_models = [m for m in models_to_download if m not in available_models]
        if invalid_models:
            return json.dumps({
                "success": False,
                "error": f"Invalid models: {', '.join(invalid_models)}",
                "available_models": available_models
            }, indent=2)
        
        # Download models
        results = []
        success_count = 0
        
        for model_name in models_to_download:
            logger.info(f"Processing model: {model_name}")
            result = await download_whisper_model(
                model_name,
                actual_models_dir,
                force_download=force_download
            )
            
            results.append({
                "model": model_name,
                "success": result["success"],
                "message": result.get("message", result.get("error", "Unknown error"))
            })
            
            if result["success"]:
                success_count += 1
        
        # Summary
        total_models = len(models_to_download)
        
        return json.dumps({
            "success": success_count > 0,
            "models_directory": str(actual_models_dir),
            "total_requested": total_models,
            "successful_downloads": success_count,
            "failed_downloads": total_models - success_count,
            "results": results,
            "core_ml_enabled": not skip_core_ml and os.uname().machine == "arm64",
            "recommendation": "Models downloaded successfully. You can now use them with whisper_start."
            if success_count == total_models
            else "Some models failed to download. Check the results for details."
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Error in download_model: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)