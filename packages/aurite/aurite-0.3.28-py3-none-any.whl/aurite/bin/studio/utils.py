"""
Utility functions for the Aurite Studio command.

This module provides functions for checking system dependencies, managing
frontend builds, and detecting server states.
"""

import asyncio
import logging
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

import httpx
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ...bin.dependencies import get_server_config
from .static_server import is_static_assets_available, get_static_assets_info

logger = logging.getLogger(__name__)
console = Console()


def check_system_dependencies() -> Tuple[bool, str]:
    """
    Check if Node.js and npm are available on the system.
    
    Returns:
        Tuple of (success: bool, error_message: str)
    """
    # On Windows, we need shell=True to properly resolve executables
    is_windows = platform.system() == "Windows"
    
    try:
        # Check Node.js
        node_result = subprocess.run(
            ["node", "--version"], 
            capture_output=True, 
            text=True, 
            timeout=10,
            shell=is_windows
        )
        if node_result.returncode != 0:
            return False, "Node.js is not installed or not accessible"
        
        node_version = node_result.stdout.strip()
        logger.debug(f"Found Node.js version: {node_version}")
        
        # Check npm
        npm_result = subprocess.run(
            ["npm", "--version"], 
            capture_output=True, 
            text=True, 
            timeout=10,
            shell=is_windows
        )
        if npm_result.returncode != 0:
            return False, "npm is not installed or not accessible"
        
        npm_version = npm_result.stdout.strip()
        logger.debug(f"Found npm version: {npm_version}")
        
        return True, ""
        
    except subprocess.TimeoutExpired:
        return False, "Timeout while checking Node.js/npm versions"
    except FileNotFoundError:
        return False, "Node.js or npm not found in PATH"
    except Exception as e:
        return False, f"Error checking system dependencies: {str(e)}"


def check_frontend_dependencies() -> bool:
    """
    Check if frontend workspace dependencies are installed.
    
    Returns:
        True if node_modules exists and appears complete, False otherwise
    """
    frontend_dir = Path.cwd() / "frontend"
    node_modules_dir = frontend_dir / "node_modules"
    
    if not node_modules_dir.exists():
        logger.debug("Frontend node_modules directory does not exist")
        return False
    
    # Check for key workspace packages
    api_client_dir = node_modules_dir / "@aurite" / "api-client"
    if not api_client_dir.exists():
        logger.debug("API client package not found in node_modules")
        return False
    
    logger.debug("Frontend dependencies appear to be installed")
    return True


async def install_frontend_dependencies() -> bool:
    """
    Install frontend workspace dependencies using npm install.
    
    Returns:
        True if installation succeeded, False otherwise
    """
    frontend_dir = Path.cwd() / "frontend"
    
    if not frontend_dir.exists():
        console.print("[bold red]Error:[/bold red] Frontend directory not found")
        return False
    
    console.print("[bold blue]Installing frontend dependencies...[/bold blue]")
    
    # On Windows, we need shell=True for subprocess calls
    is_windows = platform.system() == "Windows"
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Running npm install...", total=None)
            
            if is_windows:
                # On Windows, use shell=True and pass command as string
                process = await asyncio.create_subprocess_shell(
                    "npm install",
                    cwd=frontend_dir,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.STDOUT
                )
            else:
                # On Unix systems, use exec
                process = await asyncio.create_subprocess_exec(
                    "npm", "install",
                    cwd=frontend_dir,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.STDOUT
                )
            
            stdout, _ = await process.communicate()
            
            if process.returncode == 0:
                console.print("[bold green]✓[/bold green] Frontend dependencies installed successfully")
                return True
            else:
                console.print("[bold red]✗[/bold red] Failed to install frontend dependencies")
                if stdout:
                    console.print(f"Output: {stdout.decode()}")
                return False
                
    except Exception as e:
        console.print(f"[bold red]Error installing dependencies:[/bold red] {str(e)}")
        return False


def check_build_artifacts() -> bool:
    """
    Check if frontend build artifacts exist.
    
    Returns:
        True if api-client build exists (aurite-studio builds on-demand), False otherwise
    """
    frontend_dir = Path.cwd() / "frontend"
    
    # Check api-client build - this is the critical dependency
    api_client_dist = frontend_dir / "packages" / "api-client" / "dist"
    if not api_client_dist.exists():
        logger.debug("API client build artifacts not found")
        return False
    
    # Check for key build files in api-client dist
    index_js = api_client_dist / "index.js"
    index_dts = api_client_dist / "index.d.ts"
    
    if not (index_js.exists() and index_dts.exists()):
        logger.debug("API client build artifacts incomplete")
        return False
    
    logger.debug("API client build artifacts found")
    return True


async def build_frontend_packages() -> bool:
    """
    Build frontend workspace packages with progress display.
    
    Returns:
        True if build succeeded, False otherwise
    """
    frontend_dir = Path.cwd() / "frontend"
    
    if not frontend_dir.exists():
        console.print("[bold red]Error:[/bold red] Frontend directory not found")
        return False
    
    console.print("[bold blue]Building frontend packages...[/bold blue]")
    
    # On Windows, we need shell=True for subprocess calls
    is_windows = platform.system() == "Windows"
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Running npm run build...", total=None)
            
            if is_windows:
                # On Windows, use shell=True and pass command as string
                process = await asyncio.create_subprocess_shell(
                    "npm run build",
                    cwd=frontend_dir,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.STDOUT
                )
            else:
                # On Unix systems, use exec
                process = await asyncio.create_subprocess_exec(
                    "npm", "run", "build",
                    cwd=frontend_dir,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.STDOUT
                )
            
            stdout, _ = await process.communicate()
            
            if process.returncode == 0:
                console.print("[bold green]✓[/bold green] Frontend packages built successfully")
                return True
            else:
                console.print("[bold red]✗[/bold red] Failed to build frontend packages")
                handle_build_failure(stdout.decode() if stdout else "No output captured")
                return False
                
    except Exception as e:
        console.print(f"[bold red]Error building packages:[/bold red] {str(e)}")
        return False


def handle_build_failure(error_output: str):
    """
    Display build error information and provide helpful guidance.
    
    Args:
        error_output: The captured error output from the build process
    """
    console.print("\n[bold red]Build Failed[/bold red]")
    console.print("The frontend build process encountered an error.")
    
    if error_output.strip():
        console.print("\n[bold yellow]Build Output:[/bold yellow]")
        # Show last 20 lines of output to avoid overwhelming the user
        lines = error_output.strip().split('\n')
        if len(lines) > 20:
            console.print("... (showing last 20 lines)")
            lines = lines[-20:]
        
        for line in lines:
            console.print(f"  {line}")
    
    console.print("\n[bold blue]Troubleshooting Tips:[/bold blue]")
    console.print("1. Ensure all frontend dependencies are installed: [code]cd frontend && npm install[/code]")
    console.print("2. Try cleaning the build cache: [code]cd frontend && npm run clean[/code]")
    console.print("3. Check for TypeScript errors in the frontend code")
    console.print("4. Ensure Node.js version >= 18.0.0")


def is_api_server_running(port: Optional[int] = None) -> bool:
    """
    Check if the API server is already running.
    
    Args:
        port: Port to check. If None, uses server config port.
        
    Returns:
        True if server is running and responding, False otherwise
    """
    if port is None:
        try:
            config = get_server_config()
            port = config.PORT
        except Exception as e:
            logger.error(f"Failed to get server config: {e}")
            return False
    
    try:
        # Use httpx for async HTTP client
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"http://localhost:{port}/health")
            return response.status_code == 200
    except Exception as e:
        logger.debug(f"API server health check failed: {e}")
        return False


def is_port_in_use_by_other_service(port: int) -> bool:
    """
    Check if a port is in use by a service other than the Aurite API server.
    
    Args:
        port: Port number to check
        
    Returns:
        True if port is in use by something other than Aurite API server
    """
    # First check if port is available
    if check_port_availability(port):
        return False
    
    # Port is in use, check if it's the Aurite API server
    return not is_api_server_running(port)


def get_server_config_for_studio():
    """
    Get server configuration for studio command.
    
    Returns:
        ServerConfig instance or None if failed to load
    """
    try:
        return get_server_config()
    except RuntimeError as e:
        # RuntimeError from get_server_config already contains user-friendly message
        error_message = str(e)
        if "Server configuration error:" in error_message:
            # Extract the user-friendly part (after the prefix)
            user_message = error_message.replace("Server configuration error:", "").strip()
            console.print(f"[bold red]Configuration Error:[/bold red]")
            console.print(user_message)
        else:
            console.print(f"[bold red]Error:[/bold red] {error_message}")
        return None
    except Exception as e:
        # Fallback for any other unexpected errors
        logger.error(f"Unexpected error loading server configuration: {e}")
        console.print(f"[bold red]Error:[/bold red] Failed to load server configuration: {str(e)}")
        return None


def check_port_availability(port: int) -> bool:
    """
    Check if a port is available for use.
    
    Args:
        port: Port number to check
        
    Returns:
        True if port is available, False if in use
    """
    import socket
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            return result != 0  # Port is available if connection failed
    except Exception:
        return False


def get_workspace_root() -> Path:
    """
    Get the workspace root directory (where frontend/ is located).
    
    Returns:
        Path to workspace root
    """
    return Path.cwd()


def validate_frontend_structure() -> Tuple[bool, str]:
    """
    Validate that the frontend directory structure is correct.
    
    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    workspace_root = get_workspace_root()
    frontend_dir = workspace_root / "frontend"
    
    if not frontend_dir.exists():
        return False, "Frontend directory not found. Are you in the correct workspace?"
    
    package_json = frontend_dir / "package.json"
    if not package_json.exists():
        return False, "Frontend package.json not found"
    
    packages_dir = frontend_dir / "packages"
    if not packages_dir.exists():
        return False, "Frontend packages directory not found"
    
    api_client_dir = packages_dir / "api-client"
    studio_dir = packages_dir / "aurite-studio"
    
    if not api_client_dir.exists():
        return False, "API client package not found"
    
    if not studio_dir.exists():
        return False, "Aurite Studio package not found"
    
    return True, ""


async def rebuild_fresh_frontend() -> bool:
    """
    Perform a fresh rebuild of the frontend workspace.
    
    This mirrors the 'npm run rebuild:fresh' command:
    - Cleans all build artifacts
    - Removes node_modules cache
    - Rebuilds all packages
    
    Returns:
        True if rebuild succeeded, False otherwise
    """
    frontend_dir = Path.cwd() / "frontend"
    
    if not frontend_dir.exists():
        console.print("[bold red]Error:[/bold red] Frontend directory not found")
        return False
    
    console.print("[bold yellow]🔄 Starting fresh frontend rebuild...[/bold yellow]")
    
    try:
        # Step 1: Clean build artifacts
        console.print("[bold blue]Step 1/3:[/bold blue] Cleaning build artifacts...")
        clean_success = await clean_frontend_artifacts()
        if not clean_success:
            return False
        
        # Step 2: Remove cache
        console.print("[bold blue]Step 2/3:[/bold blue] Clearing npm cache...")
        cache_success = await clear_frontend_cache()
        if not cache_success:
            return False
        
        # Step 3: Rebuild packages
        console.print("[bold blue]Step 3/3:[/bold blue] Rebuilding packages...")
        build_success = await build_frontend_packages()
        if not build_success:
            return False
        
        console.print("[bold green]✅ Fresh frontend rebuild completed successfully![/bold green]")
        return True
        
    except Exception as e:
        console.print(f"[bold red]Error during fresh rebuild:[/bold red] {str(e)}")
        return False


async def clean_frontend_artifacts() -> bool:
    """
    Clean all frontend build artifacts.
    
    Returns:
        True if cleaning succeeded, False otherwise
    """
    frontend_dir = Path.cwd() / "frontend"
    
    # On Windows, we need shell=True for subprocess calls
    is_windows = platform.system() == "Windows"
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Running npm run clean...", total=None)
            
            if is_windows:
                # On Windows, use shell=True and pass command as string
                process = await asyncio.create_subprocess_shell(
                    "npm run clean",
                    cwd=frontend_dir,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.STDOUT
                )
            else:
                # On Unix systems, use exec
                process = await asyncio.create_subprocess_exec(
                    "npm", "run", "clean",
                    cwd=frontend_dir,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.STDOUT
                )
            
            stdout, _ = await process.communicate()
            
            if process.returncode == 0:
                console.print("[bold green]✓[/bold green] Build artifacts cleaned")
                return True
            else:
                console.print("[bold red]✗[/bold red] Failed to clean build artifacts")
                if stdout:
                    console.print(f"Output: {stdout.decode()}")
                return False
                
    except Exception as e:
        console.print(f"[bold red]Error cleaning artifacts:[/bold red] {str(e)}")
        return False


async def clear_frontend_cache() -> bool:
    """
    Clear frontend npm cache.
    
    Returns:
        True if cache clearing succeeded, False otherwise
    """
    frontend_dir = Path.cwd() / "frontend"
    cache_dir = frontend_dir / "node_modules" / ".cache"
    
    try:
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
            console.print("[bold green]✓[/bold green] npm cache cleared")
        else:
            console.print("[bold green]✓[/bold green] No cache to clear")
        
        return True
        
    except Exception as e:
        console.print(f"[bold red]Error clearing cache:[/bold red] {str(e)}")
        return False


def detect_studio_mode() -> str:
    """
    Detect whether to run studio in production (static) or development mode.
    
    Returns:
        "production" if static assets are available, "development" otherwise
    """
    if is_static_assets_available():
        return "production"
    else:
        return "development"


def is_production_mode() -> bool:
    """
    Check if studio should run in production mode (static assets).
    
    Returns:
        True if static assets are available for serving
    """
    return detect_studio_mode() == "production"


def is_development_mode() -> bool:
    """
    Check if studio should run in development mode (React dev server).
    
    Returns:
        True if should use development mode
    """
    return detect_studio_mode() == "development"


def get_studio_mode_info() -> dict:
    """
    Get detailed information about the current studio mode.
    
    Returns:
        Dictionary with mode information
    """
    mode = detect_studio_mode()
    static_info = get_static_assets_info()
    
    info = {
        "mode": mode,
        "static_assets": static_info,
        "frontend_available": validate_frontend_structure()[0],
        "node_dependencies": check_system_dependencies()[0]
    }
    
    if mode == "production":
        info["description"] = "Using pre-built static assets (production mode)"
        info["requires_nodejs"] = False
    else:
        info["description"] = "Using React development server (development mode)"
        info["requires_nodejs"] = True
    
    return info


def print_studio_mode_info():
    """
    Print information about the detected studio mode.
    """
    info = get_studio_mode_info()
    mode = info["mode"]
    
    if mode == "production":
        console.print("[bold green]✓[/bold green] Production mode: Using pre-built static assets")
        static_info = info["static_assets"]
        if static_info["available"]:
            console.print(f"[dim]Static assets: {static_info['files']} files, {static_info['size_mb']} MB[/dim]")
    else:
        console.print("[bold yellow]⚠[/bold yellow] Development mode: Will use React development server")
        if not info["node_dependencies"]:
            console.print("[bold red]✗[/bold red] Node.js dependencies required for development mode")
        if not info["frontend_available"]:
            console.print("[bold red]✗[/bold red] Frontend source code not available")
