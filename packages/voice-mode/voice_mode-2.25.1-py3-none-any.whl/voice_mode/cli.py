"""
CLI entry points for voice-mode package.
"""
import asyncio
import sys
import os
import warnings
import click

# Suppress known deprecation warnings for better user experience
# These apply to both CLI commands and MCP server operation
# They can be shown with VOICEMODE_DEBUG=true or --debug flag
if not os.environ.get('VOICEMODE_DEBUG', '').lower() in ('true', '1', 'yes'):
    # Suppress audioop deprecation warning from pydub
    warnings.filterwarnings('ignore', message='.*audioop.*deprecated.*', category=DeprecationWarning)
    # Suppress pkg_resources deprecation warning from webrtcvad
    warnings.filterwarnings('ignore', message='.*pkg_resources.*deprecated.*', category=UserWarning)
    # Suppress psutil connections() deprecation warning
    warnings.filterwarnings('ignore', message='.*connections.*deprecated.*', category=DeprecationWarning)
    
    # Also suppress INFO logging for CLI commands (but not for MCP server)
    import logging
    logging.getLogger("voice-mode").setLevel(logging.WARNING)


# Service management CLI - runs MCP server by default, subcommands override
@click.group(invoke_without_command=True)
@click.version_option()
@click.help_option('-h', '--help', help='Show this message and exit')
@click.option('--debug', is_flag=True, help='Enable debug mode and show all warnings')
@click.pass_context
def voice_mode_main_cli(ctx, debug):
    """Voice Mode - MCP server and service management.
    
    Without arguments, starts the MCP server.
    With subcommands, executes service management operations.
    """
    if debug:
        # Re-enable warnings if debug flag is set
        warnings.resetwarnings()
        os.environ['VOICEMODE_DEBUG'] = 'true'
        # Re-enable INFO logging
        import logging
        logging.getLogger("voice-mode").setLevel(logging.INFO)
    
    if ctx.invoked_subcommand is None:
        # No subcommand - run MCP server
        # Note: warnings are already suppressed at module level unless debug is enabled
        from .server import main as voice_mode_main
        voice_mode_main()


def voice_mode() -> None:
    """Entry point for voicemode command - starts the MCP server or runs subcommands."""
    voice_mode_main_cli()


# Service group commands
@voice_mode_main_cli.group()
def kokoro():
    """Manage Kokoro TTS service."""
    pass


@voice_mode_main_cli.group()
def whisper():
    """Manage Whisper STT service."""
    pass


@voice_mode_main_cli.group()
def livekit():
    """Manage LiveKit RTC service."""
    pass


# Service functions are imported lazily in their respective command handlers to improve startup time


# Kokoro service commands
@kokoro.command()
def status():
    """Show Kokoro service status."""
    from voice_mode.tools.service import status_service
    result = asyncio.run(status_service("kokoro"))
    click.echo(result)


@kokoro.command()
def start():
    """Start Kokoro service."""
    from voice_mode.tools.service import start_service
    result = asyncio.run(start_service("kokoro"))
    click.echo(result)


@kokoro.command()
def stop():
    """Stop Kokoro service."""
    from voice_mode.tools.service import stop_service
    result = asyncio.run(stop_service("kokoro"))
    click.echo(result)


@kokoro.command()
def restart():
    """Restart Kokoro service."""
    from voice_mode.tools.service import restart_service
    result = asyncio.run(restart_service("kokoro"))
    click.echo(result)


@kokoro.command()
def enable():
    """Enable Kokoro service to start at boot/login."""
    from voice_mode.tools.service import enable_service
    result = asyncio.run(enable_service("kokoro"))
    click.echo(result)


@kokoro.command()
def disable():
    """Disable Kokoro service from starting at boot/login."""
    from voice_mode.tools.service import disable_service
    result = asyncio.run(disable_service("kokoro"))
    click.echo(result)


@kokoro.command()
@click.option('--lines', '-n', default=50, help='Number of log lines to show')
def logs(lines):
    """View Kokoro service logs."""
    from voice_mode.tools.service import view_logs
    result = asyncio.run(view_logs("kokoro", lines))
    click.echo(result)


@kokoro.command("update-service-files")
def kokoro_update_service_files():
    """Update Kokoro service files to latest version."""
    from voice_mode.tools.service import update_service_files
    result = asyncio.run(update_service_files("kokoro"))
    click.echo(result)


@kokoro.command()
def health():
    """Check Kokoro health endpoint."""
    import subprocess
    try:
        result = subprocess.run(
            ["curl", "-s", "http://127.0.0.1:8880/health"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            import json
            try:
                health_data = json.loads(result.stdout)
                click.echo("✅ Kokoro is responding")
                click.echo(f"   Status: {health_data.get('status', 'unknown')}")
                if 'uptime' in health_data:
                    click.echo(f"   Uptime: {health_data['uptime']}")
            except json.JSONDecodeError:
                click.echo("✅ Kokoro is responding (non-JSON response)")
        else:
            click.echo("❌ Kokoro not responding on port 8880")
    except subprocess.TimeoutExpired:
        click.echo("❌ Kokoro health check timed out")
    except Exception as e:
        click.echo(f"❌ Health check failed: {e}")


@kokoro.command()
@click.option('--install-dir', help='Directory to install kokoro-fastapi')
@click.option('--port', default=8880, help='Port to configure for the service')
@click.option('--force', '-f', is_flag=True, help='Force reinstall even if already installed')
@click.option('--version', default='latest', help='Version to install (default: latest)')
@click.option('--auto-enable/--no-auto-enable', default=None, help='Enable service at boot/login')
def install(install_dir, port, force, version, auto_enable):
    """Install kokoro-fastapi TTS service."""
    from voice_mode.tools.services.kokoro.install import kokoro_install
    result = asyncio.run(kokoro_install.fn(
        install_dir=install_dir,
        port=port,
        force_reinstall=force,
        version=version,
        auto_enable=auto_enable
    ))
    
    if result.get('success'):
        if result.get('already_installed'):
            click.echo(f"✅ Kokoro already installed at {result['install_path']}")
            click.echo(f"   Version: {result.get('version', 'unknown')}")
        else:
            click.echo("✅ Kokoro installed successfully!")
            click.echo(f"   Install path: {result['install_path']}")
            click.echo(f"   Version: {result.get('version', 'unknown')}")
            
        if result.get('enabled'):
            click.echo("   Auto-start: Enabled")
        
        if result.get('migration_message'):
            click.echo(f"\n{result['migration_message']}")
    else:
        click.echo(f"❌ Installation failed: {result.get('error', 'Unknown error')}")
        if result.get('details'):
            click.echo(f"   Details: {result['details']}")


@kokoro.command()
@click.option('--remove-models', is_flag=True, help='Also remove downloaded Kokoro models')
@click.option('--remove-all-data', is_flag=True, help='Remove all Kokoro data including logs and cache')
@click.confirmation_option(prompt='Are you sure you want to uninstall Kokoro?')
def uninstall(remove_models, remove_all_data):
    """Uninstall kokoro-fastapi service and optionally remove data."""
    from voice_mode.tools.services.kokoro.uninstall import kokoro_uninstall
    result = asyncio.run(kokoro_uninstall.fn(
        remove_models=remove_models,
        remove_all_data=remove_all_data
    ))
    
    if result.get('success'):
        click.echo("✅ Kokoro uninstalled successfully!")
        
        if result.get('service_stopped'):
            click.echo("   Service stopped")
        if result.get('service_disabled'):
            click.echo("   Service disabled")
        if result.get('install_removed'):
            click.echo(f"   Installation removed: {result['install_path']}")
        if result.get('models_removed'):
            click.echo("   Models removed")
        if result.get('data_removed'):
            click.echo("   All data removed")
            
        if result.get('warnings'):
            click.echo("\n⚠️  Warnings:")
            for warning in result['warnings']:
                click.echo(f"   - {warning}")
    else:
        click.echo(f"❌ Uninstall failed: {result.get('error', 'Unknown error')}")
        if result.get('details'):
            click.echo(f"   Details: {result['details']}")


# Whisper service commands  
@whisper.command()
def status():
    """Show Whisper service status."""
    from voice_mode.tools.service import status_service
    result = asyncio.run(status_service("whisper"))
    click.echo(result)


@whisper.command()
def start():
    """Start Whisper service."""
    from voice_mode.tools.service import start_service
    result = asyncio.run(start_service("whisper"))
    click.echo(result)


@whisper.command()
def stop():
    """Stop Whisper service."""
    from voice_mode.tools.service import stop_service
    result = asyncio.run(stop_service("whisper"))
    click.echo(result)


@whisper.command()
def restart():
    """Restart Whisper service."""
    from voice_mode.tools.service import restart_service
    result = asyncio.run(restart_service("whisper"))
    click.echo(result)


@whisper.command()
def enable():
    """Enable Whisper service to start at boot/login."""
    from voice_mode.tools.service import enable_service
    result = asyncio.run(enable_service("whisper"))
    click.echo(result)


@whisper.command()
def disable():
    """Disable Whisper service from starting at boot/login."""
    from voice_mode.tools.service import disable_service
    result = asyncio.run(disable_service("whisper"))
    click.echo(result)


@whisper.command()
@click.option('--lines', '-n', default=50, help='Number of log lines to show')
def logs(lines):
    """View Whisper service logs."""
    from voice_mode.tools.service import view_logs
    result = asyncio.run(view_logs("whisper", lines))
    click.echo(result)


@whisper.command("update-service-files")
def whisper_update_service_files():
    """Update Whisper service files to latest version."""
    from voice_mode.tools.service import update_service_files
    result = asyncio.run(update_service_files("whisper"))
    click.echo(result)


@whisper.command()
def health():
    """Check Whisper health endpoint."""
    import subprocess
    try:
        result = subprocess.run(
            ["curl", "-s", "http://127.0.0.1:8090/health"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            import json
            try:
                health_data = json.loads(result.stdout)
                click.echo("✅ Whisper is responding")
                click.echo(f"   Status: {health_data.get('status', 'unknown')}")
                if 'uptime' in health_data:
                    click.echo(f"   Uptime: {health_data['uptime']}")
            except json.JSONDecodeError:
                click.echo("✅ Whisper is responding (non-JSON response)")
        else:
            click.echo("❌ Whisper not responding on port 8090")
    except subprocess.TimeoutExpired:
        click.echo("❌ Whisper health check timed out")
    except Exception as e:
        click.echo(f"❌ Health check failed: {e}")


@whisper.command()
@click.option('--install-dir', help='Directory to install whisper.cpp')
@click.option('--model', default='large-v2', help='Whisper model to download (default: large-v2)')
@click.option('--use-gpu/--no-gpu', default=None, help='Enable GPU support if available')
@click.option('--force', '-f', is_flag=True, help='Force reinstall even if already installed')
@click.option('--version', default='latest', help='Version to install (default: latest)')
@click.option('--auto-enable/--no-auto-enable', default=None, help='Enable service at boot/login')
def install(install_dir, model, use_gpu, force, version, auto_enable):
    """Install whisper.cpp STT service with automatic system detection."""
    from voice_mode.tools.services.whisper.install import whisper_install
    result = asyncio.run(whisper_install.fn(
        install_dir=install_dir,
        model=model,
        use_gpu=use_gpu,
        force_reinstall=force,
        version=version,
        auto_enable=auto_enable
    ))
    
    if result.get('success'):
        if result.get('already_installed'):
            click.echo(f"✅ Whisper already installed at {result['install_path']}")
            click.echo(f"   Version: {result.get('version', 'unknown')}")
        else:
            click.echo("✅ Whisper installed successfully!")
            click.echo(f"   Install path: {result['install_path']}")
            click.echo(f"   Version: {result.get('version', 'unknown')}")
            
        if result.get('gpu_enabled'):
            click.echo("   GPU support: Enabled")
        if result.get('model_downloaded'):
            click.echo(f"   Model: {result.get('model', 'unknown')}")
        if result.get('enabled'):
            click.echo("   Auto-start: Enabled")
        
        if result.get('migration_message'):
            click.echo(f"\n{result['migration_message']}")
            
        if result.get('next_steps'):
            click.echo("\nNext steps:")
            for step in result['next_steps']:
                click.echo(f"   - {step}")
    else:
        click.echo(f"❌ Installation failed: {result.get('error', 'Unknown error')}")
        if result.get('details'):
            click.echo(f"   Details: {result['details']}")


@whisper.command()
@click.option('--remove-models', is_flag=True, help='Also remove downloaded Whisper models')
@click.option('--remove-all-data', is_flag=True, help='Remove all Whisper data including logs and transcriptions')
@click.confirmation_option(prompt='Are you sure you want to uninstall Whisper?')
def uninstall(remove_models, remove_all_data):
    """Uninstall whisper.cpp and optionally remove models and data."""
    from voice_mode.tools.services.whisper.uninstall import whisper_uninstall
    result = asyncio.run(whisper_uninstall.fn(
        remove_models=remove_models,
        remove_all_data=remove_all_data
    ))
    
    if result.get('success'):
        click.echo("✅ Whisper uninstalled successfully!")
        
        if result.get('service_stopped'):
            click.echo("   Service stopped")
        if result.get('service_disabled'):
            click.echo("   Service disabled")
        if result.get('install_removed'):
            click.echo(f"   Installation removed: {result['install_path']}")
        if result.get('models_removed'):
            click.echo("   Models removed")
        if result.get('data_removed'):
            click.echo("   All data removed")
            
        if result.get('warnings'):
            click.echo("\n⚠️  Warnings:")
            for warning in result['warnings']:
                click.echo(f"   - {warning}")
    else:
        click.echo(f"❌ Uninstall failed: {result.get('error', 'Unknown error')}")
        if result.get('details'):
            click.echo(f"   Details: {result['details']}")


@whisper.command("download-model")
@click.argument('model', default='large-v2')
@click.option('--force', '-f', is_flag=True, help='Re-download even if model exists')
@click.option('--skip-core-ml', is_flag=True, help='Skip Core ML conversion on Apple Silicon')
def download_model_cmd(model, force, skip_core_ml):
    """Download Whisper model(s) with optional Core ML conversion.
    
    MODEL can be a model name (e.g., 'large-v2'), 'all' to download all models,
    or omitted to use the default (large-v2).
    
    Available models: tiny, tiny.en, base, base.en, small, small.en,
    medium, medium.en, large-v1, large-v2, large-v3, large-v3-turbo
    """
    import json
    from voice_mode.tools.services.whisper.download_model import download_model
    result = asyncio.run(download_model.fn(
        model=model,
        force_download=force,
        skip_core_ml=skip_core_ml
    ))
    
    try:
        # Parse JSON response
        data = json.loads(result)
        if data.get('success'):
            click.echo("✅ Model download completed!")
            
            if 'results' in data:
                for model_result in data['results']:
                    click.echo(f"\n📦 {model_result['model']}:")
                    if model_result.get('already_exists') and not force:
                        click.echo("   Already downloaded")
                    else:
                        click.echo("   Downloaded successfully")
                    
                    if model_result.get('core_ml_converted'):
                        click.echo("   Core ML: Converted")
                    elif model_result.get('core_ml_exists'):
                        click.echo("   Core ML: Already exists")
            
            if 'models_dir' in data:
                click.echo(f"\nModels location: {data['models_dir']}")
        else:
            click.echo(f"❌ Download failed: {data.get('error', 'Unknown error')}")
            if 'available_models' in data:
                click.echo("\nAvailable models:")
                for m in data['available_models']:
                    click.echo(f"   - {m}")
    except json.JSONDecodeError:
        click.echo(result)


# LiveKit service commands
@livekit.command()
def status():
    """Show LiveKit service status."""
    from voice_mode.tools.service import status_service
    result = asyncio.run(status_service("livekit"))
    click.echo(result)


@livekit.command()
def start():
    """Start LiveKit service."""
    from voice_mode.tools.service import start_service
    result = asyncio.run(start_service("livekit"))
    click.echo(result)


@livekit.command()
def stop():
    """Stop LiveKit service."""
    from voice_mode.tools.service import stop_service
    result = asyncio.run(stop_service("livekit"))
    click.echo(result)


@livekit.command()
def restart():
    """Restart LiveKit service."""
    from voice_mode.tools.service import restart_service
    result = asyncio.run(restart_service("livekit"))
    click.echo(result)


@livekit.command()
def enable():
    """Enable LiveKit service to start at boot/login."""
    from voice_mode.tools.service import enable_service
    result = asyncio.run(enable_service("livekit"))
    click.echo(result)


@livekit.command()
def disable():
    """Disable LiveKit service from starting at boot/login."""
    from voice_mode.tools.service import disable_service
    result = asyncio.run(disable_service("livekit"))
    click.echo(result)


@livekit.command()
@click.option('--lines', '-n', default=50, help='Number of log lines to show')
def logs(lines):
    """View LiveKit service logs."""
    from voice_mode.tools.service import view_logs
    result = asyncio.run(view_logs("livekit", lines))
    click.echo(result)


@livekit.command()
def update():
    """Update LiveKit service files to the latest version."""
    from voice_mode.tools.service import update_service_files
    result = asyncio.run(update_service_files("livekit"))
    
    if result.get("success"):
        click.echo("✅ LiveKit service files updated successfully")
        if result.get("message"):
            click.echo(f"   {result['message']}")
    else:
        click.echo(f"❌ {result.get('message', 'Update failed')}")


@livekit.command()
@click.option('--install-dir', help='Directory to install LiveKit')
@click.option('--port', default=7880, help='Port for LiveKit server (default: 7880)')
@click.option('--force', '-f', is_flag=True, help='Force reinstall even if already installed')
@click.option('--version', default='latest', help='Version to install (default: latest)')
@click.option('--auto-enable/--no-auto-enable', default=None, help='Enable service at boot/login')
def install(install_dir, port, force, version, auto_enable):
    """Install LiveKit server with development configuration."""
    from voice_mode.tools.services.livekit.install import livekit_install
    result = asyncio.run(livekit_install.fn(
        install_dir=install_dir,
        port=port,
        force_reinstall=force,
        version=version,
        auto_enable=auto_enable
    ))
    
    if result.get('success'):
        if result.get('already_installed'):
            click.echo(f"✅ LiveKit already installed at {result['install_path']}")
            click.echo(f"   Version: {result.get('version', 'unknown')}")
        else:
            click.echo("✅ LiveKit installed successfully!")
            click.echo(f"   Version: {result.get('version', 'unknown')}")
            click.echo(f"   Install path: {result['install_path']}")
            click.echo(f"   Config: {result['config_path']}")
            click.echo(f"   Port: {result['port']}")
            click.echo(f"   URL: {result['url']}")
            click.echo(f"   Dev credentials: {result['dev_key']} / {result['dev_secret']}")
            
            if result.get('service_installed'):
                click.echo("   Service installed")
                if result.get('service_enabled'):
                    click.echo("   Service enabled (will start at boot/login)")
    else:
        click.echo(f"❌ Installation failed: {result.get('error', 'Unknown error')}")
        if result.get('details'):
            click.echo(f"   Details: {result['details']}")


@livekit.command()
@click.option('--remove-config', is_flag=True, help='Also remove LiveKit configuration files')
@click.option('--remove-all-data', is_flag=True, help='Remove all LiveKit data including logs')
@click.confirmation_option(prompt='Are you sure you want to uninstall LiveKit?')
def uninstall(remove_config, remove_all_data):
    """Uninstall LiveKit server and optionally remove configuration and data."""
    from voice_mode.tools.services.livekit.uninstall import livekit_uninstall
    result = asyncio.run(livekit_uninstall.fn(
        remove_config=remove_config,
        remove_all_data=remove_all_data
    ))
    
    if result.get('success'):
        click.echo("✅ LiveKit uninstalled successfully!")
        
        if result.get('removed_items'):
            click.echo("\n📦 Removed:")
            for item in result['removed_items']:
                click.echo(f"   ✓ {item}")
                
        if result.get('warnings'):
            click.echo("\n⚠️  Warnings:")
            for warning in result['warnings']:
                click.echo(f"   - {warning}")
    else:
        click.echo(f"❌ Uninstall failed: {result.get('error', 'Unknown error')}")


# LiveKit frontend subcommands
@livekit.group()
def frontend():
    """Manage LiveKit Voice Assistant Frontend."""
    pass


@frontend.command("install")
@click.option('--auto-enable/--no-auto-enable', default=None, help='Enable service after installation (default: from config)')
def frontend_install(auto_enable):
    """Install and setup LiveKit Voice Assistant Frontend."""
    from voice_mode.tools.services.livekit.frontend import livekit_frontend_install
    result = asyncio.run(livekit_frontend_install.fn(auto_enable=auto_enable))
    
    if result.get('success'):
        click.echo("✅ LiveKit Frontend setup completed!")
        click.echo(f"   Frontend directory: {result['frontend_dir']}")
        click.echo(f"   Log directory: {result['log_dir']}")
        click.echo(f"   Node.js available: {result['node_available']}")
        if result.get('node_path'):
            click.echo(f"   Node.js path: {result['node_path']}")
        click.echo(f"   Service installed: {result['service_installed']}")
        click.echo(f"   Service enabled: {result['service_enabled']}")
        click.echo(f"   URL: {result['url']}")
        click.echo(f"   Password: {result['password']}")
        
        if result.get('service_enabled'):
            click.echo("\n💡 Frontend service is enabled and will start automatically at boot/login")
        else:
            click.echo("\n💡 Run 'voice-mode livekit frontend enable' to start automatically at boot/login")
    else:
        click.echo(f"❌ Frontend installation failed: {result.get('error', 'Unknown error')}")


@frontend.command("start")
@click.option('--port', default=3000, help='Port to run frontend on (default: 3000)')
@click.option('--host', default='127.0.0.1', help='Host to bind to (default: 127.0.0.1)')
def frontend_start(port, host):
    """Start the LiveKit Voice Assistant Frontend."""
    from voice_mode.tools.services.livekit.frontend import livekit_frontend_start
    result = asyncio.run(livekit_frontend_start.fn(port=port, host=host))
    
    if result.get('success'):
        click.echo("✅ LiveKit Frontend started successfully!")
        click.echo(f"   URL: {result['url']}")
        click.echo(f"   Password: {result['password']}")
        click.echo(f"   PID: {result['pid']}")
        click.echo(f"   Directory: {result['directory']}")
    else:
        error_msg = result.get('error', 'Unknown error')
        click.echo(f"❌ Failed to start frontend: {error_msg}")
        if "Cannot find module" in error_msg or "dependencies" in error_msg.lower():
            click.echo("")
            click.echo("💡 Try fixing dependencies with:")
            click.echo("   ./bin/fix-frontend-deps.sh")
            click.echo("   or manually: cd vendor/livekit-voice-assistant/voice-assistant-frontend && pnpm install")


@frontend.command("stop")
def frontend_stop():
    """Stop the LiveKit Voice Assistant Frontend."""
    from voice_mode.tools.services.livekit.frontend import livekit_frontend_stop
    result = asyncio.run(livekit_frontend_stop.fn())
    
    if result.get('success'):
        click.echo(f"✅ {result['message']}")
    else:
        click.echo(f"❌ Failed to stop frontend: {result.get('error', 'Unknown error')}")


@frontend.command("status")
def frontend_status():
    """Check status of the LiveKit Voice Assistant Frontend."""
    from voice_mode.tools.services.livekit.frontend import livekit_frontend_status
    result = asyncio.run(livekit_frontend_status.fn())
    
    if 'error' in result:
        click.echo(f"❌ Error: {result['error']}")
        return
    
    if result.get('running'):
        click.echo("✅ Frontend is running")
        click.echo(f"   PID: {result['pid']}")
        click.echo(f"   URL: {result['url']}")
    else:
        click.echo("❌ Frontend is not running")
    
    click.echo(f"   Directory: {result.get('directory', 'Not found')}")
    
    if result.get('configuration'):
        click.echo("   Configuration:")
        for key, value in result['configuration'].items():
            click.echo(f"     {key}: {value}")


@frontend.command("open")
def frontend_open():
    """Open the LiveKit Voice Assistant Frontend in your browser.
    
    Starts the frontend if not already running, then opens it in the default browser.
    """
    from voice_mode.tools.services.livekit.frontend import livekit_frontend_open
    result = asyncio.run(livekit_frontend_open.fn())
    
    if result.get('success'):
        click.echo("✅ Frontend opened in browser!")
        click.echo(f"   URL: {result['url']}")
        click.echo(f"   Password: {result['password']}")
        if result.get('hint'):
            click.echo(f"   💡 {result['hint']}")
    else:
        click.echo(f"❌ Failed to open frontend: {result.get('error', 'Unknown error')}")


@frontend.command("logs")
@click.option("--lines", "-n", default=50, help="Number of lines to show (default: 50)")
@click.option("--follow", "-f", is_flag=True, help="Follow log output (tail -f)")
def frontend_logs(lines, follow):
    """View LiveKit Voice Assistant Frontend logs.
    
    Shows the last N lines of frontend logs. Use --follow to tail the logs.
    """
    if follow:
        # For following, run tail -f directly
        from voice_mode.tools.services.livekit.frontend import livekit_frontend_logs
        result = asyncio.run(livekit_frontend_logs.fn(follow=True))
        if result.get('success'):
            click.echo(f"📂 Log file: {result['log_file']}")
            click.echo("🔄 Following logs (press Ctrl+C to stop)...")
            try:
                import subprocess
                subprocess.run(["tail", "-f", result['log_file']])
            except KeyboardInterrupt:
                click.echo("\n✅ Stopped following logs")
        else:
            click.echo(f"❌ Error: {result.get('error', 'Unknown error')}")
    else:
        # Show last N lines
        from voice_mode.tools.services.livekit.frontend import livekit_frontend_logs
        result = asyncio.run(livekit_frontend_logs.fn(lines=lines, follow=False))
        if result.get('success'):
            click.echo(f"📂 Log file: {result['log_file']}")
            click.echo(f"📄 Showing last {result['lines_shown']} lines:")
            click.echo("─" * 60)
            click.echo(result['logs'])
        else:
            click.echo(f"❌ Error: {result.get('error', 'Unknown error')}")


@frontend.command("enable")
def frontend_enable():
    """Enable frontend service to start automatically at boot/login."""
    from voice_mode.tools.service import enable_service
    result = asyncio.run(enable_service("frontend"))
    # enable_service returns a string, not a dict
    click.echo(result)


@frontend.command("disable")
def frontend_disable():
    """Disable frontend service from starting automatically."""
    from voice_mode.tools.service import disable_service
    result = asyncio.run(disable_service("frontend"))
    # disable_service returns a string, not a dict
    click.echo(result)


@frontend.command("build")
@click.option('--force', '-f', is_flag=True, help='Force rebuild even if build exists')
def frontend_build(force):
    """Build frontend for production (requires Node.js)."""
    import subprocess
    from pathlib import Path
    
    frontend_dir = Path(__file__).parent / "frontend"
    if not frontend_dir.exists():
        click.echo("❌ Frontend directory not found")
        return
    
    build_dir = frontend_dir / ".next"
    if build_dir.exists() and not force:
        click.echo("✅ Frontend already built. Use --force to rebuild.")
        click.echo(f"   Build directory: {build_dir}")
        return
    
    click.echo("🔨 Building frontend for production...")
    
    # Check Node.js availability
    try:
        subprocess.run(["node", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        click.echo("❌ Node.js not found. Please install Node.js to build the frontend.")
        return
    
    # Change to frontend directory and build
    import os
    original_cwd = os.getcwd()
    try:
        os.chdir(frontend_dir)
        
        # Install dependencies if needed
        if not (frontend_dir / "node_modules").exists():
            click.echo("📦 Installing dependencies...")
            subprocess.run(["npm", "install"], check=True)
        
        # Build with production settings
        click.echo("🏗️  Building standalone production version...")
        env = os.environ.copy()
        env["BUILD_STANDALONE"] = "true"
        subprocess.run(["npm", "run", "build:standalone"], check=True, env=env)
        
        click.echo("✅ Frontend built successfully!")
        click.echo(f"   Build directory: {build_dir}")
        click.echo("   Frontend will now start in production mode.")
        
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Build failed: {e}")
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}")
    finally:
        os.chdir(original_cwd)


# Configuration management group
@voice_mode_main_cli.group()
def config():
    """Manage voice-mode configuration."""
    pass


@config.command("list")
def config_list():
    """List all configuration keys with their descriptions."""
    from voice_mode.tools.configuration_management import list_config_keys
    result = asyncio.run(list_config_keys.fn())
    click.echo(result)


@config.command("get")
@click.argument('key')
def config_get(key):
    """Get a configuration value."""
    import os
    from pathlib import Path
    
    # Read from the env file
    env_file = Path.home() / ".voicemode" / "voicemode.env"
    if not env_file.exists():
        click.echo(f"❌ Configuration file not found: {env_file}")
        return
    
    # Look for the key
    found = False
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#') or not line:
                continue
            if '=' in line:
                k, v = line.split('=', 1)
                if k.strip() == key:
                    click.echo(f"{key}={v.strip()}")
                    found = True
                    break
    
    if not found:
        # Check environment variable
        env_value = os.getenv(key)
        if env_value is not None:
            click.echo(f"{key}={env_value} (from environment)")
        else:
            click.echo(f"❌ Configuration key not found: {key}")
            click.echo("Run 'voice-mode config list' to see available keys")


@config.command("set")
@click.argument('key')
@click.argument('value')
def config_set(key, value):
    """Set a configuration value."""
    from voice_mode.tools.configuration_management import update_config
    result = asyncio.run(update_config.fn(key, value))
    click.echo(result)


# Diagnostics group
@voice_mode_main_cli.group()
def diag():
    """Diagnostic tools for voice-mode."""
    pass


@diag.command()
def info():
    """Show voice-mode installation information."""
    from voice_mode.tools.diagnostics import voice_mode_info
    result = asyncio.run(voice_mode_info.fn())
    click.echo(result)


@diag.command()
def devices():
    """List available audio input and output devices."""
    from voice_mode.tools.devices import check_audio_devices
    result = asyncio.run(check_audio_devices.fn())
    click.echo(result)


@diag.command()
def registry():
    """Show voice provider registry with all discovered endpoints."""
    from voice_mode.tools.voice_registry import voice_registry
    result = asyncio.run(voice_registry.fn())
    click.echo(result)


@diag.command()
def dependencies():
    """Check system audio dependencies and provide installation guidance."""
    import json
    from voice_mode.tools.dependencies import check_audio_dependencies
    result = asyncio.run(check_audio_dependencies.fn())
    
    if isinstance(result, dict):
        # Format the dictionary output nicely
        click.echo("System Audio Dependencies Check")
        click.echo("=" * 50)
        
        click.echo(f"\nPlatform: {result.get('platform', 'Unknown')}")
        
        if 'packages' in result:
            click.echo("\nSystem Packages:")
            for pkg, status in result['packages'].items():
                symbol = "✅" if status else "❌"
                click.echo(f"  {symbol} {pkg}")
        
        if 'missing_packages' in result and result['missing_packages']:
            click.echo("\n❌ Missing Packages:")
            for pkg in result['missing_packages']:
                click.echo(f"  - {pkg}")
            if 'install_command' in result:
                click.echo(f"\nInstall with: {result['install_command']}")
        
        if 'pulseaudio' in result:
            pa = result['pulseaudio']
            click.echo(f"\nPulseAudio Status: {'✅ Running' if pa.get('running') else '❌ Not running'}")
            if pa.get('version'):
                click.echo(f"  Version: {pa['version']}")
        
        if 'diagnostics' in result and result['diagnostics']:
            click.echo("\nDiagnostics:")
            for diag in result['diagnostics']:
                click.echo(f"  - {diag}")
        
        if 'recommendations' in result and result['recommendations']:
            click.echo("\nRecommendations:")
            for rec in result['recommendations']:
                click.echo(f"  - {rec}")
    else:
        # Fallback for string output
        click.echo(str(result))


# Legacy CLI for voice-mode-cli command
@click.group()
@click.version_option()
@click.help_option('-h', '--help')
def cli():
    """Voice Mode CLI - Manage conversations, view logs, and analyze voice interactions."""
    pass


# Import subcommand groups
from voice_mode.cli_commands import exchanges as exchanges_cmd

# Add subcommands to legacy CLI
cli.add_command(exchanges_cmd.exchanges)

# Add exchanges to main CLI
voice_mode_main_cli.add_command(exchanges_cmd.exchanges)


