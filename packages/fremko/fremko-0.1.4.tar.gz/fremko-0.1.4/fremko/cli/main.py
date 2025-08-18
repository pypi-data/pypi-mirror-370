"""
Fremko CLI - Command line interface for controlling Android devices through LLM agents.
"""

from __future__ import annotations

import asyncio
import click
import os
import logging
import warnings
import time
from contextlib import nullcontext
import contextlib
from rich.console import Console
from adbutils import adb
from functools import wraps
try:
    from fremko import patch_apis
except ImportError:
    pass

from fremko.cli.logs import LogHandler
from fremko.portal import (
    download_portal_apk,
    enable_portal_accessibility,
    PORTAL_PACKAGE_NAME,
    ping_portal,
)
from fremko.ws.server import start_server
from fastapi import FastAPI
import uvicorn

from fremko.web.app import create_app

# Suppress all warnings
warnings.filterwarnings("ignore")
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["GRPC_ENABLE_FORK_SUPPORT"] = "false"

console = Console()

def configure_logging(debug: bool):
    """Configure logging for the application."""
    log_level = logging.DEBUG if debug else logging.INFO
    
    # Only configure droidrun logger
    logger = logging.getLogger("droidrun")
    logger.setLevel(log_level)
    logger.propagate = False  # prevent bubbling to root
    
    handler = LogHandler()
    formatter = logging.Formatter("%(levelname)s %(name)s %(message)s", "%H:%M:%S")
    handler.setFormatter(formatter)

    # Avoid duplicate handlers if configure_logging() is called more than once
    if not logger.handlers:
        logger.addHandler(handler)

    # Optional: silence other noisy loggers
    logging.getLogger("websockets").setLevel(logging.WARNING)
    logging.getLogger().setLevel(logging.WARNING)  # quiet everything else

def coro(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@click.group()
def cli():
    """Fremko - Control your Android device through LLM agents."""
    pass


@cli.command()
@click.option("--provider", "-p", help="LLM provider", default="GoogleGenAI")
@click.option("--model", "-m", help="LLM model name", default="models/gemini-2.5-flash")
@click.option("--temperature", type=float, help="Temperature for LLM", default=0.2)
@click.option("--steps", type=int, help="Maximum number of steps", default=150)
@click.option("--base_url", "-u", help="Base URL for API", default=None)
@click.option("--api_base", help="Base URL for API", default=None)
@click.option("--reasoning", is_flag=True, help="Enable planning with reasoning", default=True)
@click.option("--reflection", is_flag=True, help="Enable reflection", default=False)
@click.option("--tracing", is_flag=True, help="Enable tracing", default=False)
@click.option("--debug", is_flag=True, help="Enable debug logging", default=False)
@click.option("--ws-port", type=int, help="WebSocket server port", default=10001)
@click.option("--vision", is_flag=True, help="Enable vision", default=True)
@coro
async def server(
    provider: str,
    model: str,
    temperature: float,
    steps: int,
    base_url: str,
    api_base: str,
    reasoning: bool,
    reflection: bool,
    tracing: bool,
    debug: bool,
    ws_port: int,
    vision: bool,
):
    """Start the Fremko WebSocket server."""
    configure_logging(debug)
    
    agent_config = {
        "provider": provider,
        "model": model,
        "temperature": temperature,
        "steps": steps,
        "base_url": base_url,
        "api_base": api_base,
        "reasoning": reasoning,
        "reflection": reflection,
        "tracing": tracing,
        "debug": debug,
        "vision": vision, # Always enable vision for WS
    }

    try:
        await start_server(host="0.0.0.0", port=ws_port, **agent_config)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Shutting down server...[/]")
        console.print("[bold green]Server stopped.[/]")

@cli.command()
@click.option("--ws-port", type=int, help="WebSocket server port", default=10001)
@click.option("--http-port", type=int, help="HTTP server port", default=8080)
@click.option("--host", type=str, help="Bind host", default="0.0.0.0")
@click.option("--debug", is_flag=True, help="Enable debug logging", default=False)
@click.option("--provider", default="GoogleGenAI")
@click.option("--model", default="models/gemini-2.5-flash")
@click.option("--temperature", type=float, default=0.2)
@click.option("--steps", type=int, default=150)
@click.option("--base_url", type=str, default=None)
@click.option("--api_base", type=str, default=None)
@click.option("--reasoning", is_flag=True, default=True)
@click.option("--reflection", is_flag=True, default=False)
@click.option("--tracing", is_flag=True, default=False)
@click.option("--vision", is_flag=True, default=True)
@coro
async def web(
    ws_port: int,
    http_port: int,
    host: str,
    debug: bool,
    provider: str,
    model: str,
    temperature: float,
    steps: int,
    base_url: str | None,
    api_base: str | None,
    reasoning: bool,
    reflection: bool,
    tracing: bool,
    vision: bool,
):
    """Run the WebSocket server and a FastAPI web UI/HTTP API."""
    configure_logging(debug)

    agent_config = {
        "provider": provider,
        "model": model,
        "temperature": temperature,
        "steps": steps,
        "base_url": base_url,
        "api_base": api_base,
        "reasoning": reasoning,
        "reflection": reflection,
        "tracing": tracing,
        "debug": debug,
        "vision": vision,
    }

    # Start WS server task in the same loop
    ws_task = asyncio.create_task(start_server(host=host, port=ws_port, **agent_config))

    # Create FastAPI app bound to the global server instance
    app: FastAPI = create_app()

    # Run uvicorn in-process using its Server API
    config = uvicorn.Config(app, host=host, port=http_port, log_level="info")
    server = uvicorn.Server(config)
    try:
        await server.serve()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Shutting down web...[/]")
    finally:
        # Cancel the websocket server task
        if not ws_task.done():
            ws_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await ws_task


@cli.command()
def devices():
    """List connected Android devices."""
    try:
        devices = adb.list()
        if not devices:
            console.print("[yellow]No devices connected.[/]")
            return

        console.print(f"[green]Found {len(devices)} connected device(s):[/]")
        for device in devices:
            console.print(f"  • [bold]{device.serial}[/]")
    except Exception as e:
        console.print(f"[red]Error listing devices: {e}[/]")


@cli.command()
@click.argument("serial")
def connect(serial: str):
    """Connect to a device over TCP/IP."""
    try:
        device = adb.connect(serial)
        if "already connected" in device:
            console.print(f"[green]Successfully connected to {serial}[/]")
        else:
            console.print(f"[red]Failed to connect to {serial}: {device}[/]")
    except Exception as e:
        console.print(f"[red]Error connecting to device: {e}[/]")


@cli.command()
@click.argument("serial")
def disconnect(serial: str):
    """Disconnect from a device."""
    try:
        success = adb.disconnect(serial, raise_error=True)
        if success:
            console.print(f"[green]Successfully disconnected from {serial}[/]")
        else:
            console.print(f"[yellow]Device {serial} was not connected[/]")
    except Exception as e:
        console.print(f"[red]Error disconnecting from device: {e}[/]")



@cli.command()
@click.option("--device", "-d", help="Device serial number or IP address", default=None)
@click.option(
    "--path",
    help="Path to the Droidrun Portal APK to install on the device. If not provided, the latest portal apk version will be downloaded and installed.",
    default=None,
)
@click.option(
    "--debug", is_flag=True, help="Enable verbose debug logging", default=False
)
def setup(path: str | None, device: str | None, debug: bool):
    """Install and enable the DroidRun Portal on a device."""
    try:
        if not device:
            devices = adb.list()
            if not devices:
                console.print("[yellow]No devices connected.[/]")
                return

            device = devices[0].serial
            console.print(f"[blue]Using device:[/] {device}")

        device_obj = adb.device(device)
        if not device_obj:
            console.print(
                f"[bold red]Error:[/] Could not get device object for {device}"
            )
            return

        if not path:
            console.print("[bold blue]Downloading DroidRun Portal APK...[/]")
            apk_context = download_portal_apk(debug)
        else:
            console.print(f"[bold blue]Using provided APK:[/] {path}")
            apk_context = nullcontext(path)

        with apk_context as apk_path:
            if not os.path.exists(apk_path):
                console.print(f"[bold red]Error:[/] APK file not found at {apk_path}")
                return

            console.print(f"[bold blue]Step 1/2: Installing APK:[/] {apk_path}")
            try:
                device_obj.install(
                    apk_path, uninstall=True, flags=["-g"], silent=not debug
                )
            except Exception as e:
                console.print(f"[bold red]Installation failed:[/] {e}")
                return

            console.print(f"[bold green]Installation successful![/]")

            console.print(f"[bold blue]Step 2/2: Enabling accessibility service[/]")

            try:
                enable_portal_accessibility(device_obj)

                console.print("[green]Accessibility service enabled successfully![/]")
                console.print(
                    "\n[bold green]Setup complete![/] The DroidRun Portal is now installed and ready to use."
                )

            except Exception as e:
                console.print(
                    f"[yellow]Could not automatically enable accessibility service: {e}[/]"
                )
                console.print(
                    "[yellow]Opening accessibility settings for manual configuration...[/]"
                )

                device_obj.shell("am start -a android.settings.ACCESSIBILITY_SETTINGS")

                console.print(
                    "\n[yellow]Please complete the following steps on your device:[/]"
                )
                console.print(
                    f"1. Find [bold]{PORTAL_PACKAGE_NAME}[/] in the accessibility services list"
                )
                console.print("2. Tap on the service name")
                console.print(
                    "3. Toggle the switch to [bold]ON[/] to enable the service"
                )
                console.print("4. Accept any permission dialogs that appear")

                console.print(
                    "\n[bold green]APK installation complete![/] Please manually enable the accessibility service using the steps above."
                )

    except Exception as e:
        console.print(f"[bold red]Error:[/] {e}")

        if debug:
            import traceback

            traceback.print_exc()


@cli.command()
@click.option("--device", "-d", help="Device serial number or IP address", default=None)
@click.option("--debug", is_flag=True, help="Enable verbose debug logging", default=False)
def enable(device: str | None, debug: bool):
    """Enables accessibility service on a device for Fremko Portal."""
    try:
        if not device:
            devices = adb.list()
            if not devices:
                console.print("[yellow]No devices connected.[/]")
                return

            device = devices[0].serial
            console.print(f"[blue]Using device:[/] {device}")

        device_obj = adb.device(device)
        if not device_obj:
            console.print(
                f"[bold red]Error:[/] Could not get device object for {device}"
            )
            return

        try:
            enable_portal_accessibility(device_obj)
            console.print("[green]Accessibility service enabled successfully![/]")
            console.print(
                "\n[bold green]Accessibility service enabled successfully![/] The Fremko Portal is ready."
            )

        except Exception as e:
            console.print(
                f"[yellow]Could not automatically enable accessibility service: {e}[/]"
            )
            console.print(
                "[yellow]Opening accessibility settings for manual configuration...[/]"
            )

            device_obj.shell(
                "am start -a android.settings.ACCESSIBILITY_SETTINGS"
            )

            console.print(
                "\n[yellow]Please complete the following steps on your device:[/]"
            )
            console.print(
                f"1. Find [bold]{PORTAL_PACKAGE_NAME}[/] in the list"
            )
            console.print("2. Tap on the service name")
            console.print(
                "3. Toggle the switch to [bold]ON[/] to enable the service"
            )
            console.print("4. Accept any permission dialogs that appear")

    except Exception as e:
        console.print(f"[bold red]Error:[/] {e}")
        if debug:
            import traceback
            traceback.print_exc()



@cli.command()
@click.option("--device", "-d", help="Device serial number or IP address", default=None)
@click.option("--debug", is_flag=True, help="Enable verbose debug logging", default=False)
def ping(device: str | None, debug: bool):
    """Ping a device to check if it is ready and accessible."""
    try:
        device_obj = adb.device(device)
        if not device_obj:
            console.print(f"[bold red]Error:[/] Could not find device {device}")
            return

        ping_portal(device_obj, debug)
        console.print(
            "[bold green]Portal is installed and accessible. You're good to go![/]"
        )
    except Exception as e:
        console.print(f"[bold red]Error:[/] {e}")
        if debug:
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    # run server
    #server()
    web()