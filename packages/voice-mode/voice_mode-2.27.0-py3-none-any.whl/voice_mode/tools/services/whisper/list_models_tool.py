"""MCP tool for listing Whisper models."""

from voice_mode.server import mcp
from voice_mode.tools.services.whisper.list_models import list_whisper_models


@mcp.tool()
async def whisper_list_models() -> str:
    """List available Whisper models and their installation status.
    
    Shows all available Whisper models with:
    - Installation status (installed/not installed)
    - Model sizes
    - Language support
    - Currently selected model
    
    Returns:
        Formatted string showing model status and information
    """
    result = await list_whisper_models()
    
    if not result["success"]:
        return f"Error listing models: {result.get('error', 'Unknown error')}"
    
    # Format output
    output = ["Whisper Models:", ""]
    
    # Check if we should show Core ML column
    show_coreml = any(model.get("has_coreml", False) for model in result["models"])
    
    for model in result["models"]:
        # Format status indicators
        current = "→ " if model["current"] else "  "
        installed = "[✓ Installed]" if model["installed"] else "[ Download ]"
        
        # Add Core ML indicator if on macOS
        coreml = ""
        if show_coreml:
            coreml = "[ML]" if model.get("has_coreml", False) else "    "
        
        # Format model line
        line = f"{current}{model['name']:15} {installed:14} {coreml} {model['size']:>8}  {model['languages']:20}"
        if model["current"]:
            line += " (Currently selected)"
        
        output.append(line)
    
    # Add footer
    footer = [
        "",
        f"Models directory: {result['model_directory']}",
        f"Total size: {result['installed_size']} installed / {result['available_size']} available",
        "",
        f"Installed models: {result['installed_count']}/{result['total_count']}",
        f"Current model: {result['current_model']}"
    ]
    
    # Add Core ML note if on macOS
    if show_coreml:
        footer.append("")
        footer.append("[ML] = Core ML model available for faster inference on Apple Silicon")
    
    output.extend(footer)
    
    return "\n".join(output)